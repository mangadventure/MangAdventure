* **id** (*int*) - The ID of the group.
* **name** (*string*) - The name of the group.
* **description** (*string*) - The group's description.
* **website** (*string*) - The group's website.
* **discord** (*string*) - The group's Discord server.
* **twitter** (*string*) - The group's Twitter username.
* **logo** (*string*) - The group's logo.
* **members** (*array of object*) - The group's members.
  Each object contains the following:

   * **id** (*int*) - The ID of the member.
   * **name** (*string*) - The name of the member.
   * **roles** (*array of string*) - The roles of the member.
   * **twitter** (*string*) - The member's Twitter username.
   * **discord** (*string*) - The member's Discord username
     and discriminator.

* **series** (*array of object*) - The group's series.
  Each object contains the following:

   * **slug** (*slug*) - The slug of the series.
   * **title** (*string*) - The title of the series.
   * **aliases** (*array of string*) - Other names for the series.

