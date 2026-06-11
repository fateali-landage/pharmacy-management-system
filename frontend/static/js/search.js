document.addEventListener('DOMContentLoaded', function() {
    // Select elements
    const searchInput = document.querySelector('.search-input');
    const categoryFilter = document.querySelector('.category-filter');
    const statusFilter = document.querySelector('.status-filter');

    // Wire up event listeners
    if (searchInput) {
        searchInput.addEventListener('input', filterTable);
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                filterTable();
            }
        });
    }

    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterTable);
    }

    if (statusFilter) {
        statusFilter.addEventListener('change', filterTable);
    }

    // Dynamic multi-faceted filtering
    function filterTable() {
        const table = document.querySelector('table');
        if (!table) return;

        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const selectedCategory = categoryFilter ? categoryFilter.value.toLowerCase().trim() : '';
        const selectedStatus = statusFilter ? statusFilter.value.toLowerCase().trim() : '';

        // Find column indexes based on header names
        let categoryColIndex = -1;
        let statusColIndex = -1;

        const headers = Array.from(table.querySelectorAll('thead th'));
        headers.forEach((th, idx) => {
            const text = th.textContent.toLowerCase();
            if (text.includes('category') || text.includes('تصنيف') || text.includes('التصنيف')) {
                categoryColIndex = idx;
            } else if (text.includes('status') || text.includes('حالة') || text.includes('الحالة')) {
                statusColIndex = idx;
            }
        });

        const rows = table.querySelectorAll('tbody tr');
        let hasResults = false;

        rows.forEach(row => {
            // Skip the no-results row
            if (row.id === 'no-results-message') return;

            let matchesSearch = true;
            let matchesCategory = true;
            let matchesStatus = true;

            // 1) Search filter
            if (searchTerm) {
                const rowText = Array.from(row.cells)
                    .map(cell => cell.textContent.toLowerCase())
                    .join(' ');
                matchesSearch = rowText.includes(searchTerm);
            }

            // 2) Category filter
            if (selectedCategory && categoryColIndex !== -1) {
                const isAll = selectedCategory.includes('all') || selectedCategory.includes('الكل');
                if (!isAll) {
                    const cellText = row.cells[categoryColIndex].textContent.toLowerCase().trim();
                    matchesCategory = cellText.includes(selectedCategory) || selectedCategory.includes(cellText);
                }
            }

            // 3) Status filter
            if (selectedStatus && statusColIndex !== -1) {
                const isAll = selectedStatus.includes('all') || selectedStatus.includes('الكل');
                if (!isAll) {
                    const cellText = row.cells[statusColIndex].textContent.toLowerCase().trim();
                    // Robust substring-based status matching
                    if (selectedStatus.includes('low') || selectedStatus.includes('منخفض')) {
                        matchesStatus = cellText.includes('low') || cellText.includes('منخفض') || cellText.includes('quantity');
                    } else if (selectedStatus.includes('out') || selectedStatus.includes('نفاد') || selectedStatus.includes('غير متوفر')) {
                        matchesStatus = cellText.includes('out') || cellText.includes('نفاد') || cellText.includes('غير متوفر');
                    } else if (selectedStatus.includes('in') || selectedStatus.includes('available') || selectedStatus.includes('متوفر')) {
                        matchesStatus = (cellText.includes('in') || cellText.includes('available') || cellText.includes('متوفر')) 
                            && !cellText.includes('low') && !cellText.includes('out') && !cellText.includes('منخفض');
                    } else {
                        matchesStatus = cellText.includes(selectedStatus);
                    }
                }
            }

            if (matchesSearch && matchesCategory && matchesStatus) {
                row.style.display = '';
                hasResults = true;
            } else {
                row.style.display = 'none';
            }
        });

        // Show/hide no results message row
        let noResultsRow = document.getElementById('no-results-message');
        if (!hasResults) {
            if (!noResultsRow) {
                const tbody = table.querySelector('tbody');
                if (tbody) {
                    noResultsRow = document.createElement('tr');
                    noResultsRow.id = 'no-results-message';
                    const td = document.createElement('td');
                    td.colSpan = headers.length || 7;
                    td.className = 'px-6 py-8 text-center text-gray-500';
                    td.textContent = 'No matching items found';
                    noResultsRow.appendChild(td);
                    tbody.appendChild(noResultsRow);
                }
            } else {
                noResultsRow.style.display = 'table-row';
            }
        } else if (noResultsRow) {
            noResultsRow.style.display = 'none';
        }
    }
});
