let allSymptoms = [];
let selectedSymptoms = [];
const API_BASE_URL = '/api';

const symptomsList = document.getElementById('symptomsList');
const selectedList = document.getElementById('selectedList');
const symptomSearch = document.getElementById('symptomSearch');
const resultsContainer = document.getElementById('resultsContainer');
const resultsList = document.getElementById('resultsList');
const emptyState = document.getElementById('emptyState');

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('symptomsList')) {
        loadSymptoms();
        
        symptomSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = allSymptoms.filter(s => 
                s.toLowerCase().includes(query) && !selectedSymptoms.includes(s)
            );
            renderSuggestions(filtered);
        });
    }
});

async function loadSymptoms() {
    try {
        const response = await fetch(`${API_BASE_URL}/symptoms`);
        const data = await response.json();
        if (data.success) {
            allSymptoms = data.symptoms;
            renderSuggestions(allSymptoms);
        }
    } catch (error) {
        console.error('Error loading symptoms:', error);
    }
}

function renderSuggestions(symptoms) {
    symptomsList.innerHTML = '';
    
    if(symptoms.length === 0) {
        symptomsList.innerHTML = '<p style="color:#64748b; font-size:0.95rem;">No matching symptoms found.</p>';
        return;
    }

    symptoms.forEach(symptom => {
        if(selectedSymptoms.includes(symptom)) return;
        
        const chip = document.createElement('div');
        chip.className = 'symptom-chip';
        let formattedName = symptom.replace(/_/g, ' ');
        formattedName = formattedName.charAt(0).toUpperCase() + formattedName.slice(1);
        
        chip.textContent = '+ ' + formattedName;
        chip.onclick = () => addSymptom(symptom);
        symptomsList.appendChild(chip);
    });
}

function addSymptom(symptom) {
    if (!selectedSymptoms.includes(symptom)) {
        selectedSymptoms.push(symptom);
        symptomSearch.value = ''; 
        renderSelected();
        renderSuggestions(allSymptoms); 
    }
}

function removeSymptom(symptom) {
    selectedSymptoms = selectedSymptoms.filter(s => s !== symptom);
    renderSelected();
    renderSuggestions(allSymptoms);
}

function renderSelected() {
    selectedList.innerHTML = '';
    if (selectedSymptoms.length === 0) {
        selectedList.innerHTML = '<p style="color: #64748b; font-size:0.95rem; margin:auto;">No symptoms selected yet.</p>';
        return;
    }
    
    selectedSymptoms.forEach(symptom => {
        const chip = document.createElement('span');
        chip.className = 'selected-chip';
        let formattedName = symptom.replace(/_/g, ' ');
        formattedName = formattedName.charAt(0).toUpperCase() + formattedName.slice(1);
        
        chip.innerHTML = `${formattedName} <i class="fas fa-times" onclick="removeSymptom('${symptom}')"></i>`;
        selectedList.appendChild(chip);
    });
}

function clearSymptoms() {
    selectedSymptoms = [];
    renderSelected();
    renderSuggestions(allSymptoms);
    resultsContainer.classList.add('hidden');
    emptyState.classList.remove('hidden');
}

async function predictDisease() {
    if (selectedSymptoms.length < 3) {
        alert("Please select at least 3 symptoms for an accurate diagnosis.");
        return;
    }
    
    emptyState.innerHTML = '<div class="spinner"></div><p style="margin-top:15px; color:#64748b; font-weight: 500;">Analyzing symptom patterns...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symptoms: selectedSymptoms })
        });
        const data = await response.json();

        if (data.success) {
            displayResults(data.predictions);
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error('Prediction error:', error);
    }
}

function displayResults(predictions) {
    emptyState.classList.add('hidden');
    resultsContainer.classList.remove('hidden');
    resultsList.innerHTML = '';

    predictions.forEach((prediction) => {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        const precautionsHTML = prediction.precautions.length > 0
            ? `<ul class="precautions-list">${prediction.precautions.map(p => `<li>${p.charAt(0).toUpperCase() + p.slice(1)}</li>`).join('')}</ul>`
            : '<p style="color:#64748b; font-size:0.95rem;">No specific precautions listed.</p>';

        card.innerHTML = `
            <div class="result-header">
                <div class="disease-name">${prediction.disease}</div>
                <div class="confidence-badge"><i class="fas fa-check-circle"></i> ${prediction.confidence}% Match</div>
            </div>
            <div class="result-description">${prediction.description}</div>
            <div style="margin-top: 20px;">
                <strong style="color: var(--text-main); font-size: 1rem; display:block; margin-bottom: 10px;">Recommended Action:</strong>
                ${precautionsHTML}
            </div>
        `;
        resultsList.appendChild(card);
    });
}

async function deleteHistoryRecord(id) {
    if (!confirm("Are you sure you want to delete this diagnosis record?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/history/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            const card = document.getElementById(`record-${id}`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'translateY(10px)';
                setTimeout(() => {
                    card.remove();
                    if (document.querySelectorAll('.history-card').length === 0) location.reload();
                }, 300);
            }
        } else {
            alert('Failed to delete record.');
        }
    } catch (error) {
        console.error('Delete error:', error);
    }
}