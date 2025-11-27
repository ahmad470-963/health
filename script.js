// STAP 1: DEFINIEER DE URL VAN JOUW AZURE FUNCTION APP
// Dit is de URL van jouw API die de data ontvangt.
// Voor Azure Static Web Apps is dit een relatief pad via de ingebouwde proxy.
const apiUrl = "/api/http_trigger";

// Wacht tot de hele DOM (HTML-structuur) is geladen voordat je JavaScript uitvoert
document.addEventListener('DOMContentLoaded', () => {
    // Koppel de event listener aan de knop na het laden van de DOM
    const verzendKnop = document.getElementById('verzend-knop');
    if (verzendKnop) {
        verzendKnop.addEventListener('click', stuurData);
    } else {
        console.error("Fout: Knop met ID 'verzend-knop' niet gevonden in de HTML.");
    }
});


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
        const response = await fetch(apiUrl, {
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
// --- NIEUWE CODE VOOR INLOGGEN ---

async function checkLoginStatus() {
    try {
        // Vraag aan Azure: "Wie is er ingelogd?"
        const response = await fetch('/.auth/me');
        const payload = await response.json();
        const user = payload.clientPrincipal; // Hier zit de info in

        const authSectie = document.getElementById('auth-sectie');

        if (user) {
            // SITUATIE: IEMAND IS INGELOGD
            console.log("Ingelogd als:", user.userDetails);
            
            // Verander de knop naar "Hallo [Naam]" en een uitlogknop
            authSectie.innerHTML = `
                <span style="margin-right: 15px; font-weight: bold;">Hallo, ${user.userDetails}</span>
                <a href="/.auth/logout" style="text-decoration: none; color: red;">Uitloggen</a>
            `;
        } else {
            // SITUATIE: NIEMAND IS INGELOGD
            console.log("Niet ingelogd.");
            // De standaard "Inloggen" knop staat er al in HTML, dus we hoeven niks te doen
        }
    } catch (error) {
        console.error("Kon login status niet controleren:", error);
    }
}

// Voer deze check direct uit zodra de pagina laadt
document.addEventListener('DOMContentLoaded', checkLoginStatus);