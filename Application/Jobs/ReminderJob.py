import asyncio
from datetime import datetime, timedelta
from OPDproject.Core.Interfaces.ILessonRepository import ILessonRepository
from OPDproject.Core.Interfaces.ITimeSlotRepository import ITimeSlotRepository
from OPDproject.Core.Interfaces.IReminderRepository import IReminderRepository
from OPDproject.Core.UseCases.Reminder.ScheduleRemindersUseCase import ScheduleRemindersUseCase
from OPDproject.Core.Entities.Reminder import Reminder

class ReminderJob:
    def __init__(
        self,
        lesson_repo: ILessonRepository,
        time_slot_repo: ITimeSlotRepository,
        reminder_repo: IReminderRepository
    ):
        self._lesson_repo = lesson_repo
        self._time_slot_repo = time_slot_repo
        self._reminder_repo = reminder_repo
        self._use_case = ScheduleRemindersUseCase(lesson_repo, time_slot_repo, reminder_repo)

    async def run(self):
        # Создаем новые напоминания
        reminders = await self._use_case.execute(hours_ahead=1)  # Напоминаем за 1 час
        print(f"Создано напоминаний: {len(reminders)}")

        # Возвращаем список DTO, которые будут использоваться для отправки уведомлений
        notifications = []
        for reminder in reminders:
            student_id = reminder.student_id
            trigger_time = reminder.trigger_time
            lesson_id = reminder.lesson_id

            notifications.append({
                'student_id': student_id,
                'lesson_id': lesson_id,
                'trigger_time': trigger_time
            })

        return notifications
