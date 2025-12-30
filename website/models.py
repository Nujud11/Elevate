
# website/models.py
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField 
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.models import Image
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from django.shortcuts import render, redirect
from wagtail.models import Page
from .forms import ContactForm 
from wagtail import blocks

from wagtail.api import APIField

@register_setting
class SiteSettings(BaseSiteSetting):
    # Keep global/brand here so every page gets the same header/footer easily
    logo = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    tagline = models.CharField(max_length=160, blank=True, default="Elevate your future — find internships & apply in one click.")
    header_bg = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    footer_bg = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    panels = [
        MultiFieldPanel([FieldPanel("logo"), FieldPanel("tagline")], heading="Brand"),
        MultiFieldPanel([FieldPanel("header_bg"), FieldPanel("footer_bg")], heading="Backgrounds"),
    ]

class LandingPage(Page):
    # Fields so editors can edit the landing page directly
    hero_title = models.CharField(max_length=160, blank=True)
    hero_lead = models.TextField(blank=True)
    cta_text = models.CharField(max_length=60, blank=True, default="Explore")
    hero_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_title"),
            FieldPanel("hero_lead"),
            FieldPanel("cta_text"),
            FieldPanel("hero_image"),
        ], heading="Homepage Hero"),
    ]


    # This tells the API which fields to show
    api_fields = [
        APIField('hero_title'),
        APIField('hero_lead'),
        APIField('cta_text'),
        APIField('hero_image'), # This will automatically format the image
    ]

    template = "website/home_page.html"
    subpage_types = ['website.AboutPage', 'website.ContactPage']
    parent_page_types = []

class ContactPage(Page):
    # Main content fields
    page_heading = models.CharField(
        max_length=255,
        blank=True,
        default="We'd love to hear from you!",
        help_text="The main heading displayed at the top of the contact page."
    )
    intro = RichTextField(
        blank=True,
        help_text="Introductory text for the contact page, displayed below the title."
    )
    thank_you_text = RichTextField(
        blank=True,
        default="Thank you for your message! We'll get back to you soon.",
        help_text="Message displayed after a successful form submission."
    )

    # Fields for the "Get in Touch" section
    working_hours_heading = models.CharField(
        max_length=100,
        blank=True,
        default="Working Hours"
    )
    working_hours_text = RichTextField(
        blank=True,
        help_text="Detailed working hours (e.g., Sunday - Thursday: 9:00 AM – 5:00 PM)"
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Primary contact email address (e.g., support@Elevate.com)"
    )
    contact_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number (e.g., +966 50 000 0000)"
    )

    # Define fields shown in the Wagtail admin
    content_panels = Page.content_panels + [
        FieldPanel('page_heading'),
        FieldPanel('intro'),
        FieldPanel('thank_you_text'),
        FieldPanel('working_hours_heading'),
        FieldPanel('working_hours_text'),
        FieldPanel('contact_email'),
        FieldPanel('contact_phone'),
    ]

    # This tells the API which fields to show
    api_fields = [
        APIField('page_heading'),
        APIField('intro'),
        APIField('thank_you_text'),
        APIField('working_hours_heading'),
        APIField('working_hours_text'),
        APIField('contact_email'),
        APIField('contact_phone'),
    ]

    # Page settings
    template = "website/contact_page.html"
    parent_page_types = ['website.LandingPage'] # Can only be created under LandingPage
    subpage_types = [] # Cannot have child pages
    max_count = 1 # Only one ContactPage allowed per parent

    # Pass the empty form to the template context for GET requests
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['form'] = ContactForm()
        return context

    # Handle form submission (POST requests)
    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                # Import necessary modules inside the method if not used elsewhere often
                from django.core.mail import send_mail
                from django.contrib import messages
                from django.conf import settings # Import settings if using DEFAULT_FROM_EMAIL

                try:
                    # Attempt to send email
                    send_mail(
                        subject=f"Contact Form: {form.cleaned_data.get('subject', 'No Subject')}", # Use .get with default
                        message=(
                            f"Name: {form.cleaned_data['full_name']}\n"
                            f"Phone: {form.cleaned_data.get('phone_number', 'N/A')}\n"
                            f"Email: {form.cleaned_data['email']}\n\n"
                            f"Message:\n{form.cleaned_data['message']}"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL, # Use default sender from settings
                        recipient_list=['njoodalobaid@gmail.com'], # <<<--- IMPORTANT: REPLACE THIS EMAIL
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"!!! Contact form email error: {e}")
                    messages.error(request, "There was an error sending your message. Please try again later.")
                else:
                    success_msg = str(self.thank_you_text) if self.thank_you_text else "Thank you for your message!"
                    messages.success(request, success_msg)    
                return redirect(request.path)

            else: # Form is invalid
                # Re-render the page, passing the invalid form to display errors
                context = self.get_context(request, *args, **kwargs)
                context['form'] = form # Overwrite empty form with the invalid one
                return render(request, self.template, context)

        # For GET requests, call the default Wagtail serve method
        return super().serve(request, *args, **kwargs)
    

class AboutSectionBlock(blocks.StructBlock):
    """A block for a standard section with a title and rich text content."""
    section_title = blocks.CharBlock(required=True, max_length=100, help_text="Title for this section (e.g., Our Mission)")
    content = blocks.RichTextBlock(required=True, help_text="Main content for this section.")
    section_id = blocks.CharBlock(required=False, max_length=50, help_text="Unique ID for linking (e.g., mission). Leave blank if not needed.")

    class Meta:
        template = "website/blocks/about_section_block.html" 
        icon = 'pilcrow'
        label = 'Content Section'

class WhatWeOfferCardBlock(blocks.StructBlock):
    """A block for one card in the 'What We Offer' section."""
    title = blocks.CharBlock(required=True, max_length=50, help_text="Card title (e.g., For Students)")
    text = blocks.TextBlock(required=True, help_text="Brief description for the card.")

    class Meta:
        icon = 'form'
        label = 'Offer Card'


class WhatWeOfferSectionBlock(blocks.StructBlock):
    """A block specifically for the three 'What We Offer' cards."""
    section_title = blocks.CharBlock(required=True, default="What We Offer", max_length=100)
    cards = blocks.ListBlock(WhatWeOfferCardBlock(), min_num=3, max_num=3) # Enforce exactly 3 cards
    section_id = blocks.CharBlock(required=False, max_length=50, help_text="Unique ID for linking (e.g., offer). Leave blank if not needed.")

    class Meta:
        template = "website/blocks/what_we_offer_block.html" # We'll create this template
        icon = 'table'
        label = 'What We Offer Section'

class AboutPage(Page):
    # Main heading and subheading
    page_heading = models.CharField(max_length=100, default="About Elevate")
    sub_heading = models.CharField(max_length=150, blank=True, default="Empowering Students. Connecting Opportunities.")

    # StreamField for flexible content sections
    body = StreamField([
        ('section', AboutSectionBlock()),
        ('what_we_offer', WhatWeOfferSectionBlock()),
    ], use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('page_heading'),
        FieldPanel('sub_heading'),
        FieldPanel('body'),
    ]

    # This tells the API which fields to show
    api_fields = [
        APIField('page_heading'),
        APIField('sub_heading'),
        APIField('body'), # StreamFields are handled automatically
    ]

    template = "website/about_page.html"
    parent_page_types = ['website.LandingPage']
    subpage_types = []
    max_count = 1




    