import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from OPDproject.Infrastructure.Config import async_session_factory
from OPDproject.Infrastructure.Repositories.LessonRepository import LessonRepository
from OPDproject.Infrastructure.Repositories.TimeSlotRepository import TimeSlotRepository
from OPDproject.Infrastructure.Repositories.ReminderRepository import ReminderRepository
from OPDproject.Application.Jobs.ReminderJob import ReminderJob

async def reminder_job_runner(bot):
    """
    Функция-обёртка для запуска ReminderJob и получения DTO, которые будут использоваться для отправки уведомлений.
    """
    async with async_session_factory() as session:
        # Создаем реализации репозиториев, используя асинхронную сессию
        lesson_repo = LessonRepository(session)
        time_slot_repo = TimeSlotRepository(session)
        reminder_repo = ReminderRepository(session)

        # Создаем экземпляр ReminderJob
        job = ReminderJob(lesson_repo, time_slot_repo, reminder_repo)

        # Получаем уведомления
        notifications = await job.run()

        # Отправляем уведомления через бота
        for notification in notifications:
            student_id = notification['student_id']
            lesson_id = notification['lesson_id']
            trigger_time = notification['trigger_time']

            # Отправка уведомления через Telegram
            message = f"Напоминание: Урок {lesson_id} начнется в {trigger_time.strftime('%H:%M')}!"
            await bot.send_message(student_id, message)
            print(f"Напоминание отправлено студенту {student_id} о занятии {lesson_id}.")

def start_reminder_scheduler(bot):
    """
    Настроить и запустить APScheduler, который вызывает reminder_job_runner() каждые 5 минут.
    """
    scheduler = AsyncIOScheduler()
    # Добавляем задачу, которая будет выполняться каждую минуту
    scheduler.add_job(reminder_job_runner, 'interval', minutes=1, args=[bot])  # Передаем bot в runner
    scheduler.start()
    print("Сервис отправки уведомлений запущен (напоминания обрабатываются каждую минуту).")
