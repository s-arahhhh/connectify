document.addEventListener('DOMContentLoaded', () => {
    const card = document.querySelector('.card');
    const gridImages = document.querySelectorAll('.grid-image');
    const expandedContent = document.querySelector('.expanded-content');

    let isExpanded = false;

    gridImages.forEach((image) => {
        image.addEventListener('click', () => {
            if (!isExpanded) {
                card.classList.add('expanded');
                expandedContent.classList.add('expanded'); 
                isExpanded = true;
            }
        });
    });

    document.addEventListener('click', (e) => {
        if (isExpanded && !card.contains(e.target) && !e.target.classList.contains('grid-image')) {
            card.classList.remove('expanded');
            expandedContent.classList.remove('expanded'); 
            isExpanded = false;
        }
    });
});
