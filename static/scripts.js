let darko = localStorage.getItem('darko') === 'true';

document.addEventListener('DOMContentLoaded', (event) => {
    if (darko) {
        document.body.classList.add('darkmode');
        document.getElementById('dmtoggle').checked = true; 
        console.log('darkness');
    } else {
        document.body.classList.remove('darkmode');
        document.getElementById('dmtoggle').checked = false; 
    }
});

function darktime() {
    console.log('darkness')
    darko = !darko
    if (darko) {
        document.body.classList.add('darkmode')
    } else {
        document.body.classList.remove('darkmode')
    }
    }
document.getElementById('dmtoggle').onclick = darktime