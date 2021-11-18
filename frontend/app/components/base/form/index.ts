/**
 * liste les composant 'custom pour ajsf (angular json schema form)'
 */

import { ListFormComponent } from './list-form.component'

const additionalWidgets = {
    'list-form': ListFormComponent,
    'string': 'text'
  }

export { ListFormComponent, additionalWidgets };