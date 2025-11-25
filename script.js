// STAP 1: VUL DE URL VAN JOUW AZURE FUNCTION APP IN!
// Dit is de URL van jouw API die de data ontvangt. 

const { jsx } = require("react/jsx-runtime");

// Je vindt deze URL in de Azure Portal op de Overview pagina van je Function App.
const apiUrl = "/api/http_trigger";


async function stuurData() {
    // 1. Data verzamelen en valideren
    const hartslag = document.getElementById('hartslag').value;
    const slaapuren = document.getElementById('slaapuren').value;
    const stappen = document.getElementById('stappen').value;
    const adviesOutput = document.getElementById('advies-output');


 if (!hartslag || !slaapuren || !stappen) {
        adviesOutput.innerHTML = '<p style="color: red;">Vul alle velden in!</p>';
        return;
    }

    const data = {
        HeartRate: parseFloat(hartslag),
        SleepHours: parseFloat(slaapuren),
        StepsPerDay: parseInt(stappen, 10)
    };

    try {
        adviesOutput.innerHTML = '<p>Advies wordt geladen...</p>';
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const result = await response.json();
        adviesOutput.innerHTML = `<p>${result.advice}</p>`;

    } catch (error) {
        console.error('Fout bij het versturen van data:', error);
        adviesOutput.innerHTML = `<p style="color: red;">Er is een fout opgetreden: ${error.message}. Controleer de console voor details.</p>`;
    }
}