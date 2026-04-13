from django.urls import path
from personal_training.views.client.client_plan_view import ClientPlanView
from personal_training.views.client.client_trainer_assignment_view import ClientTrainerAssignmentView
from personal_training.views.client.session_cancellation_view import SessionCancellationView
from personal_training.views.admin.training_plans_view import TrainingPlanAdminView
from personal_training.views.admin.training_plan_detail import TrainingPlanAdminDetailView
from personal_training.views.client.public_training_plan_view import PublicTrainingPlanListView
from personal_training.views.client.public_plan_detail_view import PublicTrainingPlanDetailView
from personal_training.views.booking.session_type_selection_view import SessionTypeSelectionView
from personal_training.views.booking.slot_selection_view import SlotSelectionView
from personal_training.views.booking.trainer_selection_view import TrainerSelectionView
from personal_training.views.booking.start_date_selection_view import StartDateSelectionView
from personal_training.views.booking.confirm_assingment_view import ConfirmAssignmentView
from personal_training.views.client.client_current_plan_view import ClientCurrentPlanView
from personal_training.views.trainer.trainer_sessions_list_view import TrainerSessionListView
from personal_training.views.trainer.trainer_session_detail_view import TrainerSessionDetailView
from personal_training.views.video.session_video_token_view import SessionVideoTokenAPIView
from personal_training.views.client.payment_view import CreateCheckoutSessionView
from .views.video.start_session_view import StartSessionAPIView
from .views.video.end_session_view import EndSessionAPIView
from .views.video.recording_view import RecordingWebhookAPIView

from personal_training.views.stripe.stripe_webhook import stripe_webhook

urlpatterns = [
    path("plan/",ClientPlanView.as_view()),
    path("cancellations/",SessionCancellationView.as_view()),
    path("admin/training-plans/", TrainingPlanAdminView.as_view()),
    path("public/training-plans/", PublicTrainingPlanListView.as_view()),
    path("admin/training-plans/<uuid:plan_id>/",TrainingPlanAdminDetailView.as_view()),
    path("training-plans/<uuid:plan_id>/",PublicTrainingPlanDetailView.as_view()),
    path("session-type/",SessionTypeSelectionView.as_view()),
    path("select-slot/",SlotSelectionView.as_view()),
    path("select-trainer/",TrainerSelectionView.as_view()),
    path("select-startdate/",StartDateSelectionView.as_view()),
    path("confirm-assignment/",ConfirmAssignmentView.as_view()),
    path("my-current-plan/",ClientCurrentPlanView.as_view()),
    path("trainers/sessions/",TrainerSessionListView.as_view()),
    path("trainers/sessions/<int:session_id>/",TrainerSessionDetailView.as_view()),
    path("sessions/<int:session_id>/video-token/",SessionVideoTokenAPIView.as_view()),
    path("payments/checkout/",CreateCheckoutSessionView.as_view()),
    path("stripe/webhook/", stripe_webhook),
    path("sessions/<int:session_id>/start/",StartSessionAPIView.as_view(),name="start-session"),
    path("sessions/<int:session_id>/end/",EndSessionAPIView.as_view(),name="end-session"),
    path("sessions/recording-webhook/",RecordingWebhookAPIView.as_view(),name="recording-webhook"),
    

]
