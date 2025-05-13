document.addEventListener("DOMContentLoaded", function () {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(triggerEl => new bootstrap.Tooltip(triggerEl));
});
$(document).ready(function () {
    $('.django-select2').select2() // Apply select2 to all select elements
})


function resetForm(event) {
    event.preventDefault();

    const form = event.target;
    form.reset();
    form.querySelectorAll('input').forEach((input) => {
        input.value = '';
    });
    form.querySelectorAll('select option').forEach((option) => {
        option.selected = false;
    });
    form.submit()
}


//  Student/Course detail pages
function calculateAmount(selectMonth) {
    const modal = document.querySelector(`#editEnrollmentModal${selectMonth.getAttribute('forPayment')}`)
    const price = Number(modal.querySelector(`#priceInp${selectMonth.getAttribute('forPayment')}`).value)
    const discount = Number(modal.querySelector(`#dicountInp${selectMonth.getAttribute('forPayment')}`).value)

    const result = (price - ((price / 100) * discount)) * Number(selectMonth.value)
    modal.querySelector(`#amountInp${selectMonth.getAttribute('forPayment')}`).value = result
}

function openEnrollmentTab(btn) {
    let modal = document.querySelector(`#editEnrollmentModal${btn.getAttribute('enrollment_id')}`)
    modal.querySelectorAll('.mytab').forEach((t) => {
        t.classList.add('d-none')
    })
    modal.querySelector(`.mytab.${btn.getAttribute('for')}`).classList.remove('d-none')
    modal.querySelectorAll('.tab-btn').forEach((t) => {
        t.classList.remove('active')
    })
    btn.classList.add('active')
}

function paymentFromEnter(inp, enrollment_id) {
    let endDateInp = document.querySelector(`#endInp${enrollment_id}`)
    endDateInp.removeAttribute('disabled')
    if (inp.value > endDateInp.value) {
        endDateInp.value = ''
    }
    endDateInp.min = inp.value
}


// Marking Students in attendance
function markStudent(status, stid, session_id) {
    const studentData = document.querySelector(`.students-attendance-list#session${session_id} tr[stid='${stid}']`)
    studentData.setAttribute('status', status);
    studentData.querySelector(`#statusInp${stid}`).value = status;
}

function unmarkStudent(stid, session_id) {
    const studentData = document.querySelector(`.students-attendance-list#session${session_id} tr[stid='${stid}']`)
    studentData.setAttribute('status', '');
    studentData.querySelector(`#statusInp${stid}`).value = '';
}

document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', (f) => {
        f.preventDefault()
        f.target.querySelector('button[type="submit"]').disabled = true
        f.target.submit()
    })
})

function setMultipleWeekdays(selector){
    let weekdaysFieldDiv = document.getElementById('weekdays-wrapper-div')
    if (String(selector.value) == '3') {
        weekdaysFieldDiv.classList.remove('d-none')
    }else{
        weekdaysFieldDiv.classList.add('d-none')
    }
}

function manualPaymentDatesCheckbox(element){
    let targetDiv = document.getElementById(element.getAttribute('forDiv'))
    let startInp = targetDiv.querySelector('input[name="start_date"]')
    if (element.checked){
        startInp.removeAttribute('required')
        targetDiv.classList.remove('show')
    }else{
        targetDiv.classList.add('show')
        startInp.setAttribute('required', "")
    }
    console.log(startInp)
}