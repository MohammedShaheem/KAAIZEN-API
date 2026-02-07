from django.utils.timezone import now
from django.db.models import Count, Sum
from datetime import timedelta

from trainers.models import TrainerProfile
from personal_training.models import (
    TrainingSession,
    ClientTrainerAssignment,
    ClientPlan,
)


class TrainerDashboardService:

    @staticmethod
    def get_dashboard_summary(user):
        trainer = TrainerProfile.objects.get(user=user)

        today = now().date()
        week_start = today - timedelta(days=7)
        month_start = today.replace(day=1)

       
        active_clients_count = (
            ClientTrainerAssignment.objects
            .filter(trainer=trainer, is_active=True)
            .count()
        )

        
        sessions_today = TrainingSession.objects.filter(
            trainer=trainer,
            session_date=today
        ).count()

        weekly_sessions = TrainingSession.objects.filter(
            trainer=trainer,
            session_date__gte=week_start
        ).count()

        
        upcoming_sessions = (
            TrainingSession.objects
            .filter(
                trainer=trainer,
                session_date__gte=today,
                status="scheduled"
            )
            .select_related("client")
            .order_by("session_date", "start_time")[:5]
        )

        
        monthly_earnings = (
            ClientPlan.objects
            .filter(
                client__trainer_assignment__trainer=trainer,
                is_active=True,
                created_at__gte=month_start
            )
            .aggregate(total=Sum("plan__price"))
            .get("total") or 0
        )

        
        total_possible_sessions = weekly_sessions + 10  
        utilization = (
            int((weekly_sessions / total_possible_sessions) * 100)
            if total_possible_sessions > 0 else 0
        )

        return {
            "stats": {
                "active_clients": active_clients_count,
                "sessions_today": sessions_today,
                "weekly_sessions": weekly_sessions,
                "monthly_earnings": monthly_earnings,
                "schedule_utilization": utilization,
            },
            "upcoming_sessions": upcoming_sessions,
            "trainer": {
                "full_name": trainer.full_name,
                "is_verified": trainer.is_verified,
            }
        }
