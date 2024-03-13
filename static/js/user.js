document.addEventListener('DOMContentLoaded', function() {
    function previewImage(event) {
        var reader = new FileReader();
        reader.onload = function() {
            var output = document.getElementById('image-preview');
            output.src = reader.result;
            // Hide the placeholder text when an image is selected
            placeholderText.style.display = 'none';
        };
        reader.readAsDataURL(event.target.files[0]);
    }

    // Get the placeholder text element
    var placeholderText = document.getElementById('placeholder-text');

    // Add an event listener for the file input
    document.getElementById('file').addEventListener('change', function(e) {
        // Check if a file was selected
        if (e.target.files.length > 0) {
            // Preview the selected image
            previewImage(e);
        } else {
            // Reset the src of the image preview
            var output = document.getElementById('image-preview');
            output.src = '';
            // Show the placeholder text when no image is selected
            placeholderText.style.display = 'block';
        }
    });
});