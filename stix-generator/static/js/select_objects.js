document.addEventListener('DOMContentLoaded', function () {
    const stixObjects = document.querySelectorAll('.stix-object');
    const selectedList = document.getElementById('selected-list');
    const generateGraphButton = document.getElementById('generate-graph');
    const copyJsonButton = document.getElementById('copy-json');
    const flipButton = document.getElementById('flip-button');
    const flipContainer = document.querySelector('.flip-container');

    stixObjects.forEach(button => {
        button.addEventListener('click', function () {
            const objectName = this.getAttribute('data-object');
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                removeEntityInput(objectName);
            } else {
                this.classList.add('selected');
                addEntityInput(objectName);
            }
        });
    });

    generateGraphButton.addEventListener('click', function () {
        const formData = new FormData();
        const inputs = selectedList.querySelectorAll('input');

        inputs.forEach(input => {
            formData.append(input.name, input.value);
        });

        if (inputs.length === 0) {
            alert('Select at least one STIX entity first.');
            return;
        }

        generateGraphButton.disabled = true;
        generateGraphButton.textContent = 'Generating...';

        fetch('/generate-graph', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                let bundleData = data.stix_bundle;
                if (typeof bundleData === 'string') {
                    bundleData = JSON.parse(bundleData);
                }
                document.getElementById('json-output').textContent = JSON.stringify(bundleData, null, 2);
                renderMetrics(data.metrics);
                document.getElementById('story-output').innerHTML = data.story
                    ? `<h4>Story:</h4><p>${data.story}</p>`
                    : '<h4>Story:</h4><p>Not generated (no LLM configured - set OPENAI_API_KEY to enable).</p>';
            })
            .catch(error => console.error('Error:', error))
            .finally(() => {
                generateGraphButton.disabled = false;
                generateGraphButton.textContent = 'Generate Graph';
            });
    });

    copyJsonButton.addEventListener('click', function () {
        const jsonOutput = document.getElementById('json-output').textContent;
        navigator.clipboard.writeText(jsonOutput).then(() => {
            alert('JSON copied to clipboard');
        }).catch(err => {
            console.error('Error in copying text: ', err);
        });
    });

    flipButton.addEventListener('click', function () {
        flipContainer.classList.toggle('flipped');
        this.textContent = flipContainer.classList.contains('flipped') ? 'Show Bundle' : 'Show Story/Metrics';
    });

    function renderMetrics(metrics) {
        const output = document.getElementById('metrics-output');
        if (!metrics) {
            output.innerHTML = '';
            return;
        }
        const distribution = Object.entries(metrics.object_type_distribution || {})
            .map(([type, n]) => `<li>${type}: ${n}</li>`)
            .join('');
        output.innerHTML = `
            <h4>Metrics</h4>
            <ul>
                <li>Total objects: ${metrics.total_objects}</li>
                <li>Completeness: ${Number(metrics.completeness_score).toFixed(1)}%</li>
                <li>Consistency (stix2-validator): ${Number(metrics.consistency_score).toFixed(1)}%</li>
                <li>Timeliness: ${Number(metrics.timeliness_score).toFixed(1)}%</li>
                <li>Relationship ratio: ${Number(metrics.relationship_ratio).toFixed(2)}</li>
            </ul>
            <h4>Object types</h4>
            <ul>${distribution}</ul>`;
    }

    function addEntityInput(objectName) {
        const entityDiv = document.createElement('div');
        entityDiv.classList.add('entity');
        entityDiv.id = objectName + '-container';

        const label = document.createElement('label');
        label.htmlFor = `${objectName}-count`;
        label.textContent = `${capitalizeFirstLetter(objectName)} Count:`;

        const input = document.createElement('input');
        input.type = 'number';
        input.id = `${objectName}-count`;
        input.name = `${objectName}-count`;
        input.min = '1';
        input.value = '1';

        entityDiv.appendChild(label);
        entityDiv.appendChild(input);
        selectedList.appendChild(entityDiv);
    }

    function removeEntityInput(objectName) {
        const entityDiv = document.getElementById(objectName + '-container');
        if (entityDiv) {
            selectedList.removeChild(entityDiv);
        }
    }

    function capitalizeFirstLetter(string) {
        return string
            .split('-')
            .map(part => part.charAt(0).toUpperCase() + part.slice(1))
            .join(' ');
    }
});
