document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the STIX data from local storage
    const stixData = JSON.parse(localStorage.getItem('stixData'));

    if (stixData) {
        const graphContainer = document.getElementById('graph-container');

        // Initialize stixview with extended configuration options
        stixview.init(graphContainer, {
            showSidebar: true,          // Enable sidebar with object details
            enableMouseZoom: true,      // Enable zooming with the mouse wheel
            enablePanning: true,        // Enable panning
            showLabels: true,           // Display labels on nodes
            minZoom: 0.3,               // Set minimum zoom level
            maxZoom: 2.5,               // Set maximum zoom level
            graphWidth: '100%',         // Full width of the container
            graphHeight: 600,           // Graph height in pixels
            showFooter: true,           // Show footer with download links
            showMarkingNodes: true,     // Show marking definition nodes
            showTlpAsTags: true,        // Show TLP marking definition as tags on entities
            showIdrefs: false           // Show placeholder objects for mentioned IDs
            // Additional configuration options can be added here
        });

        // Load the STIX data into the graph
        stixview.loadData(stixData);

        // Optionally, remove the stored data to prevent reuse
        localStorage.removeItem('stixData');
    } else {
        console.error('No STIX data found in local storage.');
    }
});

