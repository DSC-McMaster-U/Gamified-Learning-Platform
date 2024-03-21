function toggleFeatureDescriptions() {
    const features = document.querySelectorAll('.feature-card');
    const toggleBtn = document.getElementById('toggleFeatures');
    let isExpanded = toggleBtn.textContent.includes('Less'); // Determine the current state

    features.forEach(feature => {
        if (isExpanded) {
            feature.classList.remove('show-description');
            feature.style.maxHeight = '190px'; // Ensure the transition applies smoothly
        } else {
            feature.classList.add('show-description');
            feature.style.maxHeight = '500px'; // Ensure enough space for content
        }
    });

    // Toggle button text
    toggleBtn.textContent = isExpanded ? 'Show More' : 'Show Less';
}
