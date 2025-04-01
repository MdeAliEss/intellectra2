# models.py
import os
import json
import re # Import regex
import fitz  # PyMuPDF
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging # Import the logging library

# Get an instance of the logger we configured in settings.py
logger = logging.getLogger('courses.extraction')

User = get_user_model()

class Category(models.Model):
    categoryImage = models.ImageField(upload_to='images/', null=True, blank=True)
    categoryName = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.categoryName

# New model to hold extracted PDF data
class CoursePdfInternal(models.Model):
    course = models.OneToOneField(
        'Course',
        related_name='pdf_internal_data', # How to access this from Course
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=512, blank=True) # Store the filename
    # Store extracted table of contents (list of titles/orders)
    table_of_contents = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Internal Data for {self.course.title} ({self.name})"

# CourseSection now links to CoursePdfInternal
class CourseSection(models.Model):
    # Changed ForeignKey to point to CoursePdfInternal
    pdf_data = models.ForeignKey(
        CoursePdfInternal,
        related_name='sections', # How to access sections from CoursePdfInternal
        on_delete=models.CASCADE,
        null=True # Temporarily allow null for migration
    )
    title = models.CharField(max_length=500)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        # Adjust __str__ to reflect the new relationship
        return f"{self.pdf_data.course.title} - Section {self.order}: {self.title}"

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='courses/')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    file_type = models.CharField(max_length=50, choices=[('pdf', 'PDF'), ('video', 'Video')], default='video')
    duration = models.CharField(max_length=20, blank=True)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # Removed _original_file_name, CoursePdfInternal handles this now
    # Note: The OneToOneField to CoursePdfInternal is added implicitly by the relation

    def __str__(self):
        return self.title

    # --- Updated PDF Extraction Logic ---
    def extract_data_from_pdf(self):
        """
        Extracts structured sections (title, content) and a table of contents
        from the PDF file, prioritizing embedded TOC if available.
        Returns: tuple(list_of_sections, list_of_toc_entries)
        """
        if not self.file or self.file_type != 'pdf':
            logger.debug(f"Extraction skipped for {getattr(self.file, 'name', 'N/A')}: Not a PDF or no file.")
            return [], []

        sections = []
        toc = []
        file_path = None # Initialize file_path
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
            if not os.path.exists(file_path):
                logger.warning(f"PDF file not found at {file_path}")
                return [], []

            logger.info(f"Opening PDF: {file_path}")
            doc = fitz.open(file_path)

            # --- Attempt 1: Use Embedded TOC ---
            embedded_toc = doc.get_toc(simple=False)
            if embedded_toc:
                logger.info(f"Attempting extraction using embedded TOC for {self.file.name}")
                toc_sections = []
                toc_entries = []
                section_order = 0
                top_level_entries = []
                for i, entry in enumerate(embedded_toc):
                    level, title, page_num, dest = entry
                    if level == 1:
                        pos_y = dest.get('to', fitz.Point(0, 0)).y if isinstance(dest, dict) else 0
                        top_level_entries.append({
                            'title': title.strip(), 'page_idx': page_num - 1,
                            'pos_y': pos_y, 'original_index': i
                        })
                top_level_entries.sort(key=lambda x: (x['page_idx'], x['pos_y']))
                for i, entry_info in enumerate(top_level_entries):
                    title = entry_info['title']
                    start_page_idx = entry_info['page_idx']
                    start_pos_y = entry_info['pos_y']
                    end_page_idx = len(doc) - 1
                    end_pos_y = float('inf')
                    if i + 1 < len(top_level_entries):
                        next_entry = top_level_entries[i+1]
                        end_page_idx = next_entry['page_idx']
                        end_pos_y = next_entry['pos_y']
                    current_content = ""
                    for p_idx in range(start_page_idx, end_page_idx + 1):
                        if p_idx >= len(doc): break
                        page = doc.load_page(p_idx)
                        clip_y0 = start_pos_y if p_idx == start_page_idx else 0
                        clip_y1 = end_pos_y if p_idx == end_page_idx else float('inf')
                        if p_idx == start_page_idx and p_idx == end_page_idx and clip_y1 - clip_y0 < 10:
                            clip_y1 = float('inf')
                        clip_rect = fitz.Rect(page.rect.x0, clip_y0, page.rect.x1, clip_y1)
                        page_text = page.get_text(clip=clip_rect).strip()
                        if p_idx == start_page_idx and page_text.startswith(title):
                            page_text = page_text[len(title):].strip()
                        if page_text:
                            current_content += page_text + "\n"
                    if title and current_content:
                        toc_sections.append({
                            'title': title, 'content': current_content.strip(), 'order': section_order
                        })
                        toc_entries.append({'title': title, 'order': section_order})
                        section_order += 1
                if toc_sections:
                    logger.info(f"Successfully extracted {len(toc_sections)} sections using embedded TOC.")
                    doc.close()
                    return toc_sections, toc_entries
                else:
                    logger.warning("Embedded TOC found but yielded no sections. Falling back to heuristic.")

            # --- Attempt 2: Refined Heuristic Method (Fallback) ---
            logger.info(f"Using heuristic extraction for {self.file.name}")
            sections = []
            toc = []
            current_section_data = None
            section_order = 0
            MAIN_HEADING_PATTERN = re.compile(r"^(?:[IVXLCDM]+\.|[A-Z]\.|[0-9]+\.)\s+.{3,}", re.IGNORECASE)
            SUB_HEADING_PATTERN = re.compile(r"^(?:[a-z]\.|[0-9]+\.[0-9]+(?:\.[0-9]+)*)\s+.{3,}", re.IGNORECASE)
            for page_num in range(len(doc)):
                if page_num == 0 and len(doc) > 1: continue
                page = doc.load_page(page_num)
                blocks = page.get_text("blocks", sort=True)
                for b in blocks:
                    block_text = b[4].strip()
                    lines = block_text.split('\n')
                    if not lines: continue
                    first_line = lines[0].strip()
                    if not first_line or len(first_line) > 150:
                        if current_section_data:
                            current_section_data['content'] += block_text + "\n"
                        continue
                    is_potential_title = False
                    title_text = first_line
                    is_main_heading = MAIN_HEADING_PATTERN.match(first_line)
                    is_sub_heading = SUB_HEADING_PATTERN.match(first_line)
                    if is_main_heading and not is_sub_heading:
                        is_potential_title = True
                    if first_line.lower() in ["table of contents", "contents", "index", "abstract", "introduction"]:
                        if first_line.lower() != "introduction":
                            is_potential_title = False
                    if is_potential_title:
                        if current_section_data:
                            sections.append(current_section_data)
                        current_section_data = {
                            'title': title_text,
                            'content': "\n".join(lines[1:]),
                            'order': section_order
                        }
                        toc.append({'title': title_text, 'order': section_order})
                        section_order += 1
                    elif current_section_data:
                        current_section_data['content'] += block_text + "\n"
                if current_section_data:
                    sections.append(current_section_data)
                for section in sections:
                    section['content'] = re.sub(r'\n{2,}', '\n', section['content']).strip()
            doc.close()
            logger.info(f"Heuristic extraction finished. Found {len(sections)} sections.")

        except Exception as e:
            logger.error(f"Error processing PDF {file_path or getattr(self.file, 'name', 'N/A')}: {e}", exc_info=True)
            return [], []

        return sections, toc

# --- Signal Receiver (Refactored) ---

# No pre_save needed now

@receiver(post_save, sender=Course)
def process_course_pdf(sender, instance, created, **kwargs):
    """
    Processes the PDF associated with a Course instance after it's saved.
    Creates/updates CoursePdfInternal and related CourseSection objects.
    """
    should_process = False
    pdf_data_instance = None

    # Try to get existing internal data
    try:
        pdf_data_instance = instance.pdf_internal_data
    except CoursePdfInternal.DoesNotExist:
        pdf_data_instance = None

    # Case 1: New course with a PDF file
    if created and instance.file and instance.file_type == 'pdf':
        should_process = True
        logger.info(f"New course with PDF detected: {instance.title}")

    # Case 2: Existing course, file changed TO a PDF or PDF file was updated
    elif not created and instance.file and instance.file_type == 'pdf':
        # If internal data exists, check if filename changed. If not, check if file content changed (simple check).
        # A more robust check would involve file hashing.
        if pdf_data_instance:
            if pdf_data_instance.name != instance.file.name:
                should_process = True
                logger.info(f"PDF filename change detected for: {instance.title}")
            # Add a check here if you want to re-process even if filename is same (e.g., file content updated)
            # For simplicity, we only re-process on filename change or if becoming PDF
        else:
            # No previous internal data, but now it's a PDF
            should_process = True
            logger.info(f"Course updated to PDF type: {instance.title}")

    # Case 3: Course type changed FROM PDF or file removed
    elif not created and (instance.file_type != 'pdf' or not instance.file):
        if pdf_data_instance:
            logger.info(f"PDF removed or type changed for: {instance.title}. Deleting internal data.")
            pdf_data_instance.delete() # Also cascades to delete sections
            return # Stop processing

    # --- Perform Processing ---
    if should_process:
        logger.info(f"Starting PDF processing for course: {instance.title} (ID: {instance.pk})")
        try:
            # Create or get the CoursePdfInternal instance
            if not pdf_data_instance:
                pdf_data_instance = CoursePdfInternal.objects.create(course=instance)

            # Extract data
            extracted_sections, extracted_toc = instance.extract_data_from_pdf()
            logger.info(f"Extracted {len(extracted_sections)} sections and {len(extracted_toc)} TOC entries.")

            # Update CoursePdfInternal fields
            pdf_data_instance.name = instance.file.name
            pdf_data_instance.table_of_contents = extracted_toc
            pdf_data_instance.save() # Save name and toc

            # Delete old sections before creating new ones
            pdf_data_instance.sections.all().delete()

            # Create CourseSection objects linked to pdf_data_instance
            for section_data in extracted_sections:
                CourseSection.objects.create(
                    pdf_data=pdf_data_instance, # Link to the internal data object
                    title=section_data['title'],
                    content=section_data['content'],
                    order=section_data['order']
                )
            logger.info(f"Successfully processed and saved sections for course: {instance.title}")
        except Exception as e:
            logger.error(f"Error in process_course_pdf signal for course {instance.pk}: {e}", exc_info=True)
