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
    const lessons_input_wrapper = document.getElementById(`customLessonsCountWrapper${selectMonth.getAttribute('forPayment')}`)
    const lessons_input = lessons_input_wrapper.querySelector('input#id_lessons_count')
    if (selectMonth.value == 0) {
        lessons_input_wrapper.classList.remove('d-none')
        lessons_input.removeAttribute('hidden')
        lessons_input.setAttribute('required', '')
    } else {
        lessons_input_wrapper.classList.add('d-none')
        lessons_input.setAttribute('hidden', '')
        lessons_input.removeAttribute('required')
    }
    const modal = document.querySelector(`#editEnrollmentModal${selectMonth.getAttribute('forPayment')}`)
    const price = Number(modal.querySelector(`#priceInp${selectMonth.getAttribute('forPayment')}`).value)
    const discount = Number(modal.querySelector(`#dicountInp${selectMonth.getAttribute('forPayment')}`).value)

    const result = (price - ((price / 100) * discount)) * Number(selectMonth.value)
    modal.querySelector(`#amountInp${selectMonth.getAttribute('forPayment')}`).value = result
}

function customLessonsOninput(element) {
    element.value = element.value.replace(/[^0-9]/g, '')
    const modal = document.querySelector(`#editEnrollmentModal${element.getAttribute('forPayment')}`)
    const price = Number(modal.querySelector(`#priceInp${element.getAttribute('forPayment')}`).value)
    const discount = Number(modal.querySelector(`#dicountInp${element.getAttribute('forPayment')}`).value)
    const result = ((price / 12) - ((price / 100) * discount)) * Number(element.value)
    modal.querySelector(`#amountInp${element.getAttribute('forPayment')}`).value = result.toFixed(2)
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

document.querySelectorAll('form:not(.noBtn)').forEach((form) => {
    form.addEventListener('submit', (f) => {
        f.preventDefault()
        f.target.querySelector('button[type="submit"]').disabled = true
        f.target.submit()
    })
})

function setMultipleWeekdays(selector) {
    let weekdaysFieldDiv = document.getElementById('weekdays-wrapper-div')
    if (String(selector.value) == '3') {
        weekdaysFieldDiv.classList.remove('d-none')
    } else {
        weekdaysFieldDiv.classList.add('d-none')
    }
}

function manualPaymentDatesCheckbox(element) {
    let targetDiv = document.getElementById(element.getAttribute('forDiv'))
    let startInp = targetDiv.querySelector('input[name="start_date"]')
    if (element.checked) {
        startInp.removeAttribute('required')
        targetDiv.classList.remove('show')
    } else {
        targetDiv.classList.add('show')
        startInp.setAttribute('required', "")
    }
    console.log(startInp)
}

function keydownHandler(e) {
    const key = e.key || e.keyCode;
    const isEsc = key === 'Escape' || key === 'Esc' || key === 27;

    const t = e.target;
    const isTyping =
        t && (t.isContentEditable ||
            /^(INPUT|TEXTAREA|SELECT)$/i.test(t.tagName));

    if (isEsc && !isTyping) {
        document.removeEventListener('keydown', keydownHandler);
        window.location.assign(urlOnESC); // or window.location.href = url;
    }
}

if (typeof urlOnESC !== 'undefined'){
    document.addEventListener('keydown', keydownHandler);
}

// flatpickr('input[type="date"]', {
//     dateFormat: "Y-m-d",
// })

// handle Form submit

function showAlert(status, message){
  const container = document.getElementById('message-container');

  const alertEl = document.createElement('div');
  alertEl.className = `alert alert-${status} p-1 mb-2 ps-3 d-flex align-items-center alert-dismissible fade show`;
  alertEl.setAttribute('role', 'alert');

  const span = document.createElement('span');
  span.textContent = message; // safe text ✅

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn-close position-relative p-2 ms-4 shadow-none';
  btn.setAttribute('data-bs-dismiss', 'alert');
  btn.setAttribute('aria-label', 'Close');

  alertEl.append(span, btn);
  container.appendChild(alertEl);

  setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
        bsAlert.close();
      }, 2000);
}

function getCookie(name){
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
}

async function handleFormSubmit(event) {

    event.preventDefault();
    const form = event.target
    let formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    let url = `${window.location.origin}${form.getAttribute('action')}`

    const response = await fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify(data),
      });
    const result = await response.json();

    if (response.ok){
        showAlert('success', result.message)
        form.classList.add('success')
        setTimeout(() => {
            form.classList.remove('success')
            }, 2000);
    }else{
        showAlert('danger', result.message)
        form.classList.add('error')
        setTimeout(() => {
            form.classList.remove('error')
            }, 2000);
    }
}