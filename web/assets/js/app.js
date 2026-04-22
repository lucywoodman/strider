// Form fields to cache in localStorage
const cachedFields = ['goalType', 'goalAmount', 'distanceUnit', 'currentProgress', 'targetDate', 'currentAverage'];

// Restore cached values on load
cachedFields.forEach(id => {
    const saved = localStorage.getItem(id);
    if (saved) {
        document.getElementById(id).value = saved;
    }
});

// Fall back to today if no cached date
if (!localStorage.getItem('targetDate')) {
    document.getElementById('targetDate').valueAsDate = new Date();
}

// Show/hide distance unit based on restored goalType
toggleUnits();

// Save form values on input change
cachedFields.forEach(id => {
    document.getElementById(id).addEventListener('change', function () {
        localStorage.setItem(id, this.value);
    });
});

function toggleUnits() {
    const goalType = document.getElementById('goalType').value;
    const distanceUnitGroup = document.getElementById('distanceUnitGroup');

    distanceUnitGroup.style.display = goalType === 'distance' ? '' : 'none';
}

document.getElementById('calculatorForm').addEventListener('submit', function(e) {
    e.preventDefault();
    calculateTarget();
});

function calculateTarget() {
    // Get form values
    const goalType = document.getElementById('goalType').value;
    const goalAmount = parseFloat(document.getElementById('goalAmount').value);
    const currentProgress = parseFloat(document.getElementById('currentProgress').value);
    const targetDate = new Date(document.getElementById('targetDate').value);
    const stepsPerKm = parseFloat(localStorage.getItem('stepsPerKm')) || 1400;
    const walkingSpeed = parseFloat(localStorage.getItem('walkingSpeed')) || 5.0;
    const distanceUnit = document.getElementById('distanceUnit').value;
    const currentAverageInput = document.getElementById('currentAverage').value;
    const currentAverage = currentAverageInput ? parseFloat(currentAverageInput) : null;

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    targetDate.setHours(0, 0, 0, 0);

    // Calculate days remaining (including today)
    const msPerDay = 24 * 60 * 60 * 1000;
    const daysRemaining = Math.ceil((targetDate - today) / msPerDay) + 1;

    if (daysRemaining <= 0) {
        showError("Target date must be in the future!");
        return;
    }

    // Convert everything to steps for calculation
    let goalSteps = goalAmount;
    let currentSteps = currentProgress;

    if (goalType === 'distance') {
        const kmMultiplier = distanceUnit === 'miles' ? 1.60934 : 1;
        goalSteps = goalAmount * kmMultiplier * stepsPerKm;
        currentSteps = currentProgress * kmMultiplier * stepsPerKm;
    }

    const stepsRemaining = goalSteps - currentSteps;
    const dailyStepsNeeded = stepsRemaining / daysRemaining;
    const dailyKmNeeded = dailyStepsNeeded / stepsPerKm;
    const dailyTimeNeeded = dailyKmNeeded / walkingSpeed;

    // Generate results HTML
    let resultsHTML = '';

    if (stepsRemaining <= 0) {
        resultsHTML = `
            <div class="result-card">
                <div class="result-header" data-variant="success">
                    🎉 Congratulations! You've already achieved your goal!
                </div>
            </div>
            <button class="button" onclick="showForm()">Recalculate</button>
        `;
    } else {
        const isAchievable = dailyStepsNeeded <= 25000; // Reasonable daily limit
        const alertClass = isAchievable ? 'success' : 'warning';
        const alertIcon = isAchievable ? '✅' : '⚠️';

        // Check if daily target exceeds 2x the current average
        let warningHTML = '';
        if (currentAverage !== null && dailyStepsNeeded > 2 * currentAverage) {
            warningHTML = `
                <div class="result-row">
                    <span class="result-label" style="color: var(--warning);">⚠️ This requires more than doubling your current average of ${Math.round(currentAverage).toLocaleString()} steps/day.</span>
                </div>
            `;
        }

        resultsHTML = `
            <div class="result-card">
                <div class="result-header" data-variant="${alertClass}">
                    ${alertIcon} ${isAchievable ? 'Achievable!' : 'Challenging!'}
                </div>
                <div class="result-row">
                    <span class="result-label">Steps remaining</span>
                    <span class="result-value">${Math.ceil(stepsRemaining).toLocaleString()}</span>
                </div>
                <div class="result-row">
                    <span class="result-label">Days remaining</span>
                    <span class="result-value">${daysRemaining}</span>
                </div>
                <div class="result-row">
                    <span class="result-label">Daily steps needed</span>
                    <span class="result-value">${Math.ceil(dailyStepsNeeded).toLocaleString()}</span>
                </div>
                <div class="result-row">
                    <span class="result-label">Daily distance</span>
                    <span class="result-value">${dailyKmNeeded.toFixed(1)} km</span>
                </div>
                <div class="result-row">
                    <span class="result-label">Daily walking time</span>
                    <span class="result-value">${Math.floor(dailyTimeNeeded)}h ${Math.round((dailyTimeNeeded % 1) * 60)}min</span>
                </div>
                ${warningHTML}
            </div>

            <button class="button" onclick="showForm()">Recalculate</button>
        `;
    }

    document.getElementById('resultsContent').innerHTML = resultsHTML;
    document.getElementById('calculatorForm').setAttribute('hidden', '');
    document.getElementById('results').removeAttribute('hidden');
}

function showError(message) {
    const resultsHTML = `
        <div class="result-card">
            <div class="result-header" data-variant="warning">
                ⚠️ ${message}
            </div>
        </div>
        <button class="button" onclick="showForm()">Back</button>
    `;
    document.getElementById('resultsContent').innerHTML = resultsHTML;
    document.getElementById('calculatorForm').setAttribute('hidden', '');
    document.getElementById('results').removeAttribute('hidden');
}

function showForm() {
    document.getElementById('results').setAttribute('hidden', '');
    document.getElementById('calculatorForm').removeAttribute('hidden');
}
