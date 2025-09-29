from aiogram.handlers import BaseHandler
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime
import os
from django.conf import settings

from .utils import RegistrationForm, ChatState
from .keyboards import confirm_button, request_phone_keyboard, st_data_keyboard, students_inline_keyboard_builder, get_main_menu_keyboard, subjects_inline_keyboard_builder, teachers_inline_keyboard_builder, about_center_inline_keyboard
from .database import get_user, add_user
from .helpers import get_students, get_enrollments, get_enrollment_balance, get_student, get_enrollment_attendance_list, get_subjects, get_subject_teachers, get_teacher_info
from .messages import about_center_text

router = Router()

@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    kb = await get_main_menu_keyboard(message.from_user.id)
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "🌅 Доброе утро!"
    elif 12 <= hour < 18:
        greeting = "☀️ Добрый день!"
    elif 18 <= hour < 23:
        greeting = "🌆 Добрый вечер!"
    else:
        greeting = "🌙 Доброй ночи!"
    await message.answer(f"{greeting} Рады видеть вас здесь ✨", reply_markup=kb)
    await state.set_state(ChatState.main_menu)

@router.message(Command('help'))
async def start(message: Message, state: FSMContext):
    kb = await get_main_menu_keyboard(message.from_user.id)
    await message.answer(text="ℹ️ О боте\nЭтот бот позволяет студентам учебного центра быстро получать информацию:\n• 💳 Баланс по оплате обучения\n• ✅ Посещаемость занятий\n• 🏫 Дополнительные сведения о нашем учебном центре\n\n⚠️ Важно: Ваш номер телефона в Telegram должен совпадать с номером, указанным в базе студентов у администратора.\nЕсли номер не совпадает, бот не сможет показать ваши данные.", reply_markup=kb)
    await state.set_state(ChatState.main_menu)

@router.message(F.text == "🏫 О центре")
async def about_center(message: Message, state: FSMContext):
    kb = about_center_inline_keyboard()
    file_path = os.path.join(settings.STATIC_ROOT, 'img/center-img.jpg')
    photo = FSInputFile(file_path)
    await message.answer_photo(photo=photo, caption=str(about_center_text), parse_mode="HTML", reply_markup=kb)
    await state.set_state(ChatState.main_menu)

@router.message(F.text == "📖 Материалы")
async def get_materials(message: Message, state: FSMContext):
    await message.answer(text='Скоро ...')

@router.message(F.text == '🧑‍🏫 Учителя')
async def staff(message: Message, state: FSMContext):
    subjects = await get_subjects()
    data = []
    for subject in subjects:
        text = f'{subject["name"]}'
        callback_data = f'get_teachers_subject_{subject["id"]}'
        data.append({'text':text, 'callback_data':callback_data})
    kb = subjects_inline_keyboard_builder(data)
    await message.answer(text='Выберите предмет:', reply_markup=kb)

@router.callback_query(F.data.startswith("get_teachers_subject"))
async def callback_subject_teachers(call: CallbackQuery, state: FSMContext):
    subject_id = call.data.split("_")[-1]
    teachers = await get_subject_teachers(subject_id)
    if teachers and len(teachers) > 0:
        data = []
        for teacher in teachers:
            text = f'{teacher["fname"]} {teacher["lname"]}'
            callback_data = f'get_teacher_{teacher["id"]}'
            data.append({'text': text, 'callback_data': callback_data})

        kb = teachers_inline_keyboard_builder(data)
        await call.message.answer(text='Выберите Преподователя:', reply_markup=kb)
        await call.message.delete()
    else:
        await call.message.answer(text="❌ Нет Учителей")

    await call.answer()

@router.callback_query(F.data.startswith("get_teacher"))
async def callback_teacher_info(call: CallbackQuery, state: FSMContext):
    teacher_id = call.data.split("_")[-1]
    teacher = await get_teacher_info(teacher_id)

    if teacher:
        caption = f'<b>{teacher["fname"]} {teacher["lname"]}</b>\n\n{teacher["bio"]}'

        file_path = os.path.join(settings.MEDIA_ROOT, str(teacher['image']))
        photo = FSInputFile(file_path)

        await call.message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
    else:
        await call.message.answer(text="❗ Учитель не найден.")
    await call.answer()


@router.message(F.text == '🔙 Главное меню')
async def main_menu(message: Message, state: FSMContext):
    kb = await get_main_menu_keyboard(message.from_user.id)
    await message.answer(text="Главное меню", reply_markup=kb)
    await state.set_state(ChatState.main_menu)

@router.message(F.text == '🗂️ Данные Ученика')
async def st_info_menu(message: Message, state: FSMContext):
    await  message.answer(text='Выберите информацию', reply_markup=st_data_keyboard)
    await state.set_state(ChatState.student_info)

@router.message(F.text == '🔑 Войти', ChatState.main_menu)
async def sign_in(message: Message, state: FSMContext):

    user = await get_user(message.from_user.id)

    if user:
        await message.answer(f"Вы уже зарегестрированы", reply_markup=st_data_keyboard)
        await state.set_state(ChatState.student_info)
    else:
        await message.answer("📞 Пожалуйста отправьте контакт текущего профиля:",
                             reply_markup=request_phone_keyboard)
        await state.set_state(RegistrationForm.get_phone)



@router.message(F.contact, RegistrationForm.get_phone)
async def get_contact(message: Message, state: FSMContext):
    contact = message.contact
    phone_number = contact.phone_number
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    if contact.user_id != message.from_user.id:
        await message.answer("❌ Пожалуйста отправьте контакт текущего профиля Телеграм.")
        return

    students = await get_students(phone_number)

    if not students:
        kb = await get_main_menu_keyboard(message.from_user.id)
        await message.answer("❌ Этот номер не найден в системе.", reply_markup=kb)
        await state.set_state(ChatState.main_menu)
        return

    await message.answer(text=f"Найдено:\n\n{'\n'.join(['{id}. {fname} {lname}'.format(id=st['id'], fname=st['fname'], lname=st['lname']) for st in students])}")

    await state.update_data(
        phone_number=phone_number,
        first_name=contact.first_name,
        last_name=contact.last_name,
        user_id = contact.user_id
    )

    await message.answer(
        text=f"Подтверждаете ?",
        reply_markup=confirm_button
    )
    await state.set_state(RegistrationForm.confirm)


@router.message(F.text.in_(['Да', 'Нет', '✅ Да', '❌ Нет']), RegistrationForm.confirm)
async def confirm_contact(message: Message, state: FSMContext   ):
    data = await state.get_data()
    main_kb = await get_main_menu_keyboard(message.from_user.id)
    contact = {
        'phone_number' : data.get("phone_number"),
        'first_name' : data.get("first_name"),
        'last_name' : data.get("last_name"),
        'user_id' : data.get("user_id")
    }

    if message.text in ['✅ Да', 'Да']:
        user = await add_user(contact, message.from_user)
        if user:
            await message.answer(text="Вы успешно зарегисрированы 🎉", reply_markup=st_data_keyboard)
            await state.set_state(ChatState.student_info)
        else:
            await message.answer(text="Что-то пошло не так ⛔", reply_markup=main_kb)
    else:
            await message.answer(text="Действие отменено ❌", reply_markup=main_kb)

    await state.clear()

@router.message(ChatState.student_info, F.text == '💰 Баланс')
async def get_balance(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        students = await get_students(user['phone_number'])

        if students and len(students) == 1:
            student = students[0]
            enrollments = await get_enrollments(student['id'])
            text = f"{student['fname']} {student['lname']}\n\n"
            if enrollments:
                rows = []
                for enrollment in enrollments:
                    balance = await get_enrollment_balance(enrollment['id'])
                    t = f"{enrollment['course']}\n⏳ Оплачено до: {balance['payed_due'].strftime('%m/%d/%Y') if balance['payed_due'] else '---'}\n💰 Баланс: {balance['balance']}"
                    rows.append(t)

                text += '\n----\n'.join(rows)
                await message.answer(text=text)
            else:
                await message.answer("❗ Ученик никуда не записан")
        elif  students and len(students) > 1:
            kb_data = []
            for student in students:
                text = f"{student['fname']} {student['lname']}"
                callback_data = f'get_balance_{student["id"]}'
                kb_data.append({'text': text, 'callback_data':callback_data})
            kb = students_inline_keyboard_builder(kb_data)

            await message.answer(text="Выберите ученика для баланса: ", reply_markup=kb)
        else:
            kb = await get_main_menu_keyboard(message.from_user.id)
            await message.answer("❗Ученики не найдены", reply_markup=kb)
    else:
        kb = await get_main_menu_keyboard(message.from_user.id)
        await message.answer(text='Ошибка❗\nПожалуйста, попробуйте войти заново.', reply_markup=kb)


@router.callback_query(F.data.startswith("get_balance"))
async def callback_st_balance(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    if user:
        st_id = call.data.split("_")[-1]
        student = await get_student(st_id)
        if student:
            enrollments = await get_enrollments(student['id'])
            text = f"{student['fname']} {student['lname']}\n\n"
            if enrollments:
                rows = []
                for enrollment in enrollments:
                    balance = await get_enrollment_balance(enrollment['id'])
                    t = f"{enrollment['course']}\n⏳ Оплачено до: {balance['payed_due'].strftime('%m/%d/%Y') if balance['payed_due'] else '---'}\n💰 Баланс: {balance['balance']}"
                    rows.append(t)

                text += '\n----\n'.join(rows)
                await call.message.answer(text=text)
            else:
                await call.message.answer("❗ Ученик никуда не записан")
        else:
            await call.message.answer("❗ Ученик не найден")

        await call.message.delete()
    else:
        kb = await get_main_menu_keyboard(call.from_user.id)
        await call.message.answer(text='Ошибка❗\nПожалуйста, попробуйте войти заново.', reply_markup=kb)


@router.message(ChatState.student_info, F.text == '📅 Посещение')
async def get_attendance(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        students = await get_students(user['phone_number'])

        if students and len(students) == 1:
            student = students[0]
            enrollments = await get_enrollments(student['id'])
            text = f"{student['fname']} {student['lname']}\n\n"
            if enrollments:
                rows = []
                for enrollment in enrollments:
                    attendance_list = await get_enrollment_attendance_list(enrollment['id'])
                    t = f"{enrollment['course']}\n"
                    for attendance in attendance_list:
                        t += f'🗓{attendance['date'].strftime('%m/%d/%Y')} -> {attendance["status"]}\n'

                    rows.append(t)

                text += '\n----\n'.join(rows)
                await message.answer(text=text)
            else:
                await message.answer("❗ Ученик никуда не записан")

        elif  students and len(students) > 1:
            kb_data = []
            for student in students:
                text = f"{student['fname']} {student['lname']}"
                callback_data = f'get_attendance_{student["id"]}'
                kb_data.append({'text': text, 'callback_data':callback_data})
            kb = students_inline_keyboard_builder(kb_data)

            await message.answer(text="Выберите ученика для информации Посещения: ", reply_markup=kb)
    else:
        kb = await get_main_menu_keyboard(message.from_user.id)
        await message.answer(text='Ошибка❗\nПожалуйста, попробуйте войти заново.', reply_markup=kb)

@router.callback_query(F.data.startswith("get_attendance"))
async def callback_st_attendance(call: CallbackQuery, state: FSMContext):
    user = await get_user(call.from_user.id)
    if user:
        st_id = call.data.split("_")[-1]
        student = await get_student(st_id)
        if student:
            enrollments = await get_enrollments(student['id'])
            text = f"{student['fname']} {student['lname']}\n\n"
            if enrollments:
                rows = []
                for enrollment in enrollments:
                    attendance_list = await get_enrollment_attendance_list(enrollment['id'])
                    t = f"{enrollment['course']}\n"
                    for attendance in attendance_list:
                        t += f'🗓{attendance['date'].strftime('%m/%d/%Y')} -> {attendance["status"]}\n'

                    rows.append(t)

                text += '\n----\n'.join(rows)
                await call.message.answer(text=text)
            else:
                await call.message.answer("❗ Ученик никуда не записан")
        else:
            await call.message.answer("❗ Ученик не найден")

        await call.message.delete()
    else:
        kb = await get_main_menu_keyboard(call.from_user.id)
        await call.message.answer(text='Ошибка❗\nПожалуйста, попробуйте войти заново.', reply_markup=kb)
