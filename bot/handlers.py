from aiogram.handlers import BaseHandler
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.db.models import Q
from .utils import RegistrationForm
from .keyboards import confirm_button, request_phone_keyboard


from students.models import Enrollment, StudentModel

@sync_to_async
def get_enrollments(phone_number):
    results =  list(
        Enrollment.objects.filter(status=True, student__phone_number=str(phone_number)).distinct()
        .values_list("student__id", "student__first_name", "student__last_name")
    )

    return [f"{id}. {first} {last}" for id, first, last in results]

@sync_to_async
def get_students(phone_number):
    results = list(
        StudentModel.objects.filter(Q(phone_number=str(phone_number)) | Q(additional_number=str(phone_number))).values_list("id", "first_name", "last_name")
    )

    return [f"{id}-- {first} {last}" for id, first, last in results]

async def greeting(message: Message, state: FSMContext):
    await message.answer("Please verify with your phone number:",
                         reply_markup=request_phone_keyboard)
    await state.set_state(RegistrationForm.get_phone)


async def get_contact(message: Message, state: FSMContext):
    contact = message.contact

    if contact.user_id != message.from_user.id:
        await message.answer("❌ Пожалуйста отправьте контакт текущего профиля Телеграм.")
        return

    students = await get_students(contact.phone_number)

    if not students:
        await message.answer("❌ Этот номер не найден в системе.")
        return

    await message.answer(text=f"Найдено:\n\n{'\n'.join(students)}")
    await message.answer(
        text=f"{contact.phone_number} Подтверждаете ?",
        reply_markup=confirm_button
    )
    await state.set_state(RegistrationForm.confirm)

async def confirm_contact(message: Message, state: FSMContext):
    await message.answer(text="Hooray")
    await state.clear()