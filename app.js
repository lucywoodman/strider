// Set today's date as default
document.getElementById('targetDate').valueAsDate = new Date();

function toggleUnits() {
    const goalType = document.getElementById('goalType').value;
    const distanceUnitGroup = document.getElementById('distanceUnitGroup');

    if (goalType === 'distance') {
        distanceUnitGroup.classList.remove('hidden');
    } else {
        distanceUnitGroup.classList.add('hidden');
    }
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
    const stepsPerKm = parseFloat(document.getElementById('stepsPerKm').value);
    const walkingSpeed = parseFloat(document.getElementById('walkingSpeed').value);
    const distanceUnit = document.getElementById('distanceUnit').value;
    
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
    const dailyMilesNeeded = dailyKmNeeded / 1.60934;
    const dailyTimeNeeded = dailyKmNeeded / walkingSpeed;
    
    const currentDailyAverage = currentSteps / Math.max(1, Math.ceil((today - new Date(today.getFullYear(), today.getMonth(), 1)) / msPerDay));
    
    // Generate results HTML
    let resultsHTML = '';
    
    if (stepsRemaining <= 0) {
        resultsHTML = `
            <div class="box" data-box-variant="success">
                <strong>🎉 Congratulations!</strong> You've already achieved your goal!
            </div>
        `;
    } else {
        const isAchievable = dailyStepsNeeded <= 25000; // Reasonable daily limit
        const alertClass = isAchievable ? 'success' : 'warning';
        const alertIcon = isAchievable ? '✅' : '⚠️';

        resultsHTML = `
            <div class="box" data-box-variant="${alertClass}">
                <div class="stack">
                    <strong>${alertIcon} ${isAchievable ? 'Achievable!' : 'Challenging!'}</strong>
                    <p>${isAchievable
                        ? 'This target looks achievable with consistent effort.'
                        : 'This target is quite ambitious - you may want to consider if it\'s realistic for your lifestyle.'
                    }</p>
                    ${dailyStepsNeeded > currentDailyAverage * 2
                        ? `<p>Note: This requires more than doubling your current average of ${Math.round(currentDailyAverage).toLocaleString()} steps/day.</p>`
                        : ''
                    }
                </div>
            </div>

            <div class="grid" style="--grid-min-item-size: 15rem;">
                <div class="box">
                    <div class="stack stack-s">
                        <strong>Steps Remaining</strong>
                        <div class="result-value">${Math.ceil(stepsRemaining).toLocaleString()} steps</div>
                    </div>
                </div>

                <div class="box">
                    <div class="stack stack-s">
                        <strong>Days Remaining</strong>
                        <div class="result-value">${daysRemaining} days</div>
                    </div>
                </div>

                <div class="box">
                    <div class="stack stack-s">
                        <strong>Daily Steps Needed</strong>
                        <div class="result-value">${Math.ceil(dailyStepsNeeded).toLocaleString()} steps/day</div>
                    </div>
                </div>

                <div class="box">
                    <div class="stack stack-s">
                        <strong>Daily Distance Needed</strong>
                        <div class="result-value">${dailyKmNeeded.toFixed(1)} km (${dailyMilesNeeded.toFixed(1)} miles)</div>
                    </div>
                </div>

                <div class="box">
                    <div class="stack stack-s">
                        <strong>Daily Walking Time Needed</strong>
                        <div class="result-value">${Math.floor(dailyTimeNeeded)}h ${Math.round((dailyTimeNeeded % 1) * 60)}min</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    document.getElementById('resultsContent').innerHTML = resultsHTML;
    document.getElementById('results').removeAttribute('hidden');
}

function showError(message) {
    const resultsHTML = `
        <div class="box" data-box-variant="warning">
            <strong>⚠️ Error:</strong> ${message}
        </div>
    `;
    document.getElementById('resultsContent').innerHTML = resultsHTML;
    document.getElementById('results').removeAttribute('hidden');
}

function showStrideHelp() {
    const helpContent = `
        <div class="center">
            <div class="stack stack-l">
                <h2>How to Estimate Steps per Kilometre</h2>

                <h3>Quick Averages by Height:</h3>
                <ul>
                    <li><strong>Shorter (under 5'4"/163cm):</strong> ~1,500-1,600 steps/km</li>
                    <li><strong>Average (5'4"-5'10"/163-178cm):</strong> ~1,300-1,500 steps/km</li>
                    <li><strong>Taller (over 5'10"/178cm):</strong> ~1,200-1,400 steps/km</li>
                </ul>

                <h3>More Accurate Methods:</h3>
                <ul>
                    <li><strong>Walk a known distance:</strong> Find a 1km route (track, measured path) and count your steps</li>
                    <li><strong>Use a football pitch:</strong> About 100m long - walk 10 lengths and count steps, then multiply by 10</li>
                    <li><strong>Smartphone step counter:</strong> Many phones have built-in step counters you can test against known distances</li>
                </ul>

                <p><strong>Default used:</strong> 1,400 steps/km (a good average for most people)</p>
            </div>
        </div>
    `;
    document.getElementById('helpContent').innerHTML = helpContent;
    document.getElementById('helpModal').removeAttribute('hidden');
}

function showSpeedHelp() {
    const helpContent = `
        <h2>How to Estimate Walking Speed</h2>

        <h3>Typical Walking Speeds:</h3>
        <ul>
            <li><strong>Leisurely stroll:</strong> 3-4 km/h (1.9-2.5 mph)</li>
            <li><strong>Comfortable pace:</strong> 4-5 km/h (2.5-3.1 mph)</li>
            <li><strong>Brisk walk:</strong> 5-6 km/h (3.1-3.7 mph)</li>
            <li><strong>Fast walk/power walk:</strong> 6-7 km/h (3.7-4.3 mph)</li>
        </ul>

        <h3>Quick Test:</h3>
        <ul>
            <li>Time yourself walking 1km (or 0.6 miles)</li>
            <li>If it takes 12 minutes = 5 km/h</li>
            <li>If it takes 15 minutes = 4 km/h</li>
            <li>If it takes 10 minutes = 6 km/h</li>
        </ul>

        <h3>Factors that affect speed:</h3>
        <ul>
            <li>Terrain (hills, paths vs roads)</li>
            <li>Weather conditions</li>
            <li>Whether you're walking the dog (usually slower!)</li>
            <li>Your fitness level</li>
        </ul>

        <p><strong>Default used:</strong> 5 km/h (a comfortable brisk pace for most people)</p>
    `;
    document.getElementById('helpContent').innerHTML = helpContent;
    document.getElementById('helpModal').removeAttribute('hidden');
}

function closeHelp() {
    document.getElementById('helpModal').setAttribute('hidden', '');
}

window.onclick = function(event) {
    const modal = document.getElementById('helpModal');
    if (event.target === modal) {
        modal.setAttribute('hidden', '');
    }
}


