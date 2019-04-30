(function ($) {
    $(document).ready(function () {
        select = document.getElementById('id_login_type');

        if (select) {

            password1 = document.getElementById('id_password1');
            password2 = document.getElementById('id_password2');

            select.addEventListener("change", function () {
                const value = this.value;

                [].forEach.call(document.querySelectorAll('.field-password1, .field-password2'), function (el) {
                    if (value === 'LDAP') {
                        el.style.display = 'none';
                        password1.value = "LXe2XTtYZnj4YBbw"
                        password2.value = "LXe2XTtYZnj4YBbw"
                    } else {
                        el.style.display = null
                        password1.value = null;
                        password2.value = null;
                    }
                });
            });

            var event = new Event('change');
            select.dispatchEvent(event);
        }
    });
})(django.jQuery);