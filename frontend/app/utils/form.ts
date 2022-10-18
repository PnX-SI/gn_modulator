import { FormControl, FormGroup } from '@angular/forms';

const getFormErrors = (form) => {
  if (form instanceof FormControl) {
    // Return FormControl errors or null
    return form.errors ?? null;
  }
  if (form instanceof FormGroup) {
    const groupErrors = form.errors;
    // Form group can contain errors itself, in that case add'em
    const formErrors = groupErrors ? { groupErrors } : {};
    Object.keys(form.controls).forEach((key) => {
      // Recursive call of the FormGroup fields
      const error = getFormErrors(form.get(key));
      if (error !== null) {
        // Only add error if not null
        formErrors[key] = error;
      }
    });
    // Return FormGroup errors or null
    return Object.keys(formErrors).length > 0 ? formErrors : null;
  }
};

const prettyFormErrors = (form) => {
  return JSON.stringify(getFormErrors(form), null, '____');
};

export default { getFormErrors, prettyFormErrors };
