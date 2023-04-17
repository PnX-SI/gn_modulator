## Composant de choix dans une liste

### Options

- `items`: liste d'éléments
- `multiple`: choix multiple
- `return_object`: renvoie un dictionnaire (ou liste de dictionnaire)

- `api`: api source de la liste

### Exemples

#### Basiques

##### Liste simple
```
    key: items_simple
    type: list_form
    items: [a, b, c]
```

##### Liste multiple
```
    key: items_multiple
    type: list_form
    items: [a, b, c]
    multiple: true
```