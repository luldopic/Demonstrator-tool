// User roles, you can dynamically fetch this from your server
const userRoles = ['admin', 'demonstrator']; // Example roles for a user

const availableRoles = ['admin', 'lecturer', 'demonstrator'];
const roleDropdownMenu = document.getElementById('roleDropdownMenu');

function populateRoleDropdown(roles) {
    roles.forEach(role => {
        const roleItem = document.createElement('a');
        roleItem.className = 'dropdown-item';
        roleItem.href = '#';
        roleItem.textContent = role.charAt(0).toUpperCase() + role.slice(1);
        roleDropdownMenu.appendChild(roleItem);
    });
}

// Populate the dropdown menu with the user's roles
populateRoleDropdown(userRoles);
