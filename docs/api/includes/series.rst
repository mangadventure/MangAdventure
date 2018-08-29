* **slug** (*string*) - The slug of the series.
* **title** (*string*) - The title of the series.
* **aliases** (*array of string*) - Other names for the series.
* **url** (*string*) - The URL of the series.
* **description** (*string*) - The description of the series.
* **authors** (*array of array*) - The series' authors.
  Each array contains the name and aliases of the author.
* **artists** (*array of array*) - The series' artists.
  Each array contains the name and aliases of the artist.
* **cover** (*string*) - The URL of the series' cover.
* **completed** (*boolean*) - Whether the series is completed.
* **volumes** (*object*) - The volumes of the series.
  The key of each volume is its number.
  The value is an object containing the volume's chapters.
  Each chapter's key is its number and its value contains the following:

