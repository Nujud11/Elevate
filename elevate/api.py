# elevate/api.py
from typing import List, Union
from datetime import date
from ninja import Field, ModelSchema, NinjaAPI, Schema, File
from ninja.files import UploadedFile 
from wagtail.models import Page
from wagtail.rich_text import expand_db_html
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

# --- Imports ---
from ninja.security import SessionAuth


from internships.models import Internship
from website.models import AboutPage
from accounts.models import Profile, Education, Experience
from applications.models import Application
from applications.forms import ApplicationCreateForm

# --- Wagtail API Router (This is correct) ---
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet

api_router = WagtailAPIRouter('wagtailapi')
api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)


# --- Django Ninja API ---
api = NinjaAPI(auth=SessionAuth(), csrf=True)

# -----------------------------------------------
# Schemas
# -----------------------------------------------

class MessageSchema(Schema):
    message: str

class InternshipSchema(ModelSchema):
    class Config:
        model = Internship
        model_fields = ['id', 'title', 'location', 'is_remote', 'description', 'deadline']

class InternshipCreateSchema(Schema):
    title: str
    location: str
    is_remote: bool = False
    description: str
    deadline: date = None

class EducationSchema(ModelSchema):
    class Config:
        model = Education
        model_fields = ['id', 'school_name', 'degree', 'start_date', 'end_date']

class ExperienceSchema(ModelSchema):
    class Config:
        model = Experience
        model_fields = ['id', 'company_name', 'role', 'start_date', 'end_date', 'description']

class StudentProfileSchema(ModelSchema):
    education: List[EducationSchema] = Field(..., alias="education.all")
    experience: List[ExperienceSchema] = Field(..., alias="experience.all")
    class Config:
        model = Profile
        model_fields = ['full_name', 'bio', 'language', 'linkedin_url', 'twitter_url', 'website_url', 'avatar', 'cv']

class CompanyProfileSchema(ModelSchema):
    class Config:
        model = Profile
        model_fields = ['full_name', 'bio', 'language', 'linkedin_url', 'twitter_url', 'website_url', 'avatar']

class SimpleStudentProfileSchema(ModelSchema):
    username: str = Field(..., alias="user.username")
    class Config:
        model = Profile
        model_fields = ['full_name', 'avatar']

class ApplicationSchema(ModelSchema):
    student: SimpleStudentProfileSchema = Field(..., alias="student.profile")
    internship: InternshipSchema
    class Config:
        model = Application
        model_fields = ['id', 'status', 'submitted_at', 'cv', 'cover_letter']

# --- Wagtail Page Schemas ---
class BasePageSchema(ModelSchema):
    url: str = Field(None, alias="get_url")
    class Config:
        model = Page
        model_fields = ["id", "title", "slug"]

class AboutPageSchema(BasePageSchema):
    page_heading: str
    sub_heading: str
    
    # --- THIS IS THE FIX ---
    # We tell Ninja that the 'body' field is of type 'str'
    body: str 
    # --- END OF FIX ---

    class Config(BasePageSchema.Config):
        model = AboutPage
        # We only include fields that are *not* StreamFields here
        model_fields = ['page_heading', 'sub_heading']
    
    # This resolver will now be called for the 'body' field
    @staticmethod
    def resolve_body(page: AboutPage) -> str:
        # We add 'context' as the second argument, which Ninja expects
        return expand_db_html(page.body)

# -----------------------------------------------
# API Endpoints
# -----------------------------------------------

# --- Public Endpoints ---
@api.get("/internships", response=List[InternshipSchema], auth=None)
def list_internships(request):
    return Internship.objects.filter(is_active=True)

@api.get("/pages/about", response=AboutPageSchema, auth=None) 
def get_about_page(request):
    return get_object_or_404(AboutPage.objects.live(), slug='about-us').specific

# --- Secured Profile Endpoints ---
@api.get("/profile/me", response={200: Union[StudentProfileSchema, CompanyProfileSchema], 401: MessageSchema, 403: MessageSchema})
def get_my_profile(request):
    return request.user.profile

# --- Secured Student Endpoints ---
@api.post("/internships/{internship_id}/apply", response={200: MessageSchema, 400: MessageSchema, 401: MessageSchema, 403: MessageSchema, 404: MessageSchema})
def apply_for_internship(request, internship_id: int, cv: UploadedFile = File(...), cover_letter: UploadedFile = File(None)):
    if not request.user.profile.is_student:
        return 403, {"message": "Only students can apply"}
    internship = get_object_or_404(Internship, id=internship_id, is_active=True)
    if Application.objects.filter(internship=internship, student=request.user).exists():
        return 400, {"message": "You have already applied to this internship"}
    form_data = {} 
    form_files = {'cv': cv}
    if cover_letter:
        form_files['cover_letter'] = cover_letter
    form = ApplicationCreateForm(form_data, form_files)
    if not form.is_valid():
        return 400, {"message": f"Invalid file: {form.errors.as_text()}"}
    application = form.save(commit=False)
    application.internship = internship
    application.student = request.user
    application.save()
    return 200, {"message": "Application submitted successfully"}

@api.get("/profile/me/applications", response={200: List[ApplicationSchema], 401: MessageSchema, 403: MessageSchema})
def get_my_applications(request):
    if not request.user.profile.is_student:
        return 403, {"message": "Only students have applications"}
    apps = Application.objects.filter(student=request.user).select_related('internship', 'student__profile')
    return apps

# --- Secured Company Endpoints ---
@api.post("/internships", response={200: InternshipSchema, 401: MessageSchema, 403: MessageSchema})
def create_internship(request, payload: InternshipCreateSchema):
    if not request.user.profile.is_company:
        return 403, {"message": "You do not have permission to post internships"}
    data = payload.dict()
    internship = Internship.objects.create(
        owner=request.user,
        **data
    )
    return internship

@api.get("/profile/me/internships", response={200: List[InternshipSchema], 401: MessageSchema, 403: MessageSchema})
def get_my_internships(request):
    if not request.user.profile.is_company:
        return 403, {"message": "Only companies have internships"}
    internships = Internship.objects.filter(owner=request.user)
    return internships

@api.get("/internships/{internship_id}/applications", response={200: List[ApplicationSchema], 401: MessageSchema, 403: MessageSchema, 404: MessageSchema})
def get_internship_applications(request, internship_id: int):
    if not request.user.profile.is_company:
        return 403, {"message": "Permission denied"}
    internship = get_object_or_404(Internship, id=internship_id)
    if internship.owner != request.user:
        return 403, {"message": "You do not own this internship"}
    apps = Application.objects.filter(internship=internship).select_related('internship', 'student__profile')
    return apps
