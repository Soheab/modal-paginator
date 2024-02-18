.. currentmodule:: discord.ext.modal_paginator

.. _whats_new:

Changelog
============

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

v1.2.0
-------

Features
~~~~~~~~

- :commit:`8c329efcc3fc4ea69fae03d0e31e39f48b3e5280` Added two new kwargs to :meth:`.ModalPaginator.send` :

  * ``add_page_string``

  * ``return_message``

  See the kwarg's docstring for more information.

- :commit:`4b959be5a52ec7c763e300a2a631f180fc9509c1` :meth:`.ModalPaginator.from_text_inputs` can now take a list of :class:`str`
  (or mixed with :class:`.discord.ui.TextInput`) instead of a list of :class:`.discord.ui.TextInput`. This is useful
  if you don't want to construct a :class:`.discord.ui.TextInput`.

- :commit:`f7a164f7503e36e5c1aee0480d0d9630478104ba` Added a new property to :class:`.PaginatorModal`:

  * :attr:`.PaginatorModal.text_inputs`

  This is also used in :meth:`.ModalPaginator.text_inputs`.

  See the property's docstring for more information.

Bug Fixes
~~~~~~~~~

- :commit:`8c329efcc3fc4ea69fae03d0e31e39f48b3e5280` ``**kwargs`` in :meth:`.ModalPaginator.send` are now properly passed to the destination.

v1.1.1
------

Miscellaneous
~~~~~~~~~~~~~~

- :commit:`92d852a51cc38e0e2135d1521dd80b7c7d1e434c` Bumped the minimum discord.py version required. From `2.0.0` to `2.2.0`.


v1.1.0
-------

Features
~~~~~~~~~

- :commit:`e13542080b9902216baa33f609531f992f53eca4` Added the ability to have the paginator automatically "finish" the paginator. 
  See the :attr:`.ModalPaginator.auto_finish` attribute for more 
  information.
- :commit:`ace7bceb6ce6b4d33a70863209b9030ed59942eb` Added a method to have the extension construct the amount of modals needed depending 
  on the needed :class:`~discord.ui.TextInput`\s. See :meth:`.ModalPaginator.from_text_inputs`
  for more information.
- :commit:`d4111ffd5bc9c6d31acb40e8fb5e607aeea9d6c0` Added the ability to customize the "error" message that users could get when they used a button
  that they weren't supposed to use (yet). This is useful for i18n purposes or to 
  send a friendlier message overal. See the following methods on :class:`.ModalPaginator` for more information:

  * :meth:`~.ModalPaginator.get_open_button_error_message`
  * :meth:`~.ModalPaginator.get_next_button_error_message`
  * :meth:`~.ModalPaginator.get_previous_button_error_message`
  * :meth:`~.ModalPaginator.get_finish_button_error_message`

Bug Fixes
~~~~~~~~~

- :commit:`2f032a5a6df32f1a46450a7a56ce4db425818b4a` Fix not being able to remove a "default" button using the ``buttons=`` kwarg.

Miscellaneous
~~~~~~~~~~~~~

- :commit:`228711cdc1cb9aaa6987a406f44577cb2ad23570` You no longer have to call the original implementation of :meth:`.ModalPaginator.on_finish` / :meth:`.ModalPaginator.on_cancel`
  when overriding it. It's now called automatically.
- :commit:`8507c52d0ca9c0ed51980a6a19f6bc230632b643` Refactored the custom buttons implementation to work better front and-backend.
- :commit:`bc1850b2a84bf87c7a2275b752233da183a09f4e` Made it so your implementation of :meth:`.ModalPaginator.on_finish` / :meth:`.ModalPaginator.on_cancel` 
  is called first before the default implementation.
- :commit:`3ecfcaf7af2bf00ae9a8a53c8f3955e51a9af0d3` Fix typo in the docstring of :attr:`.ModalPaginator.message`.
- :commit:`3ecfcaf7af2bf00ae9a8a53c8f3955e51a9af0d3` Fix the example for the ``buttons`` kwarg on :class:`.ModalPaginator` in the
  docstring.


v1.0.0
-------

- First stable release!
- Added the ability to customize the buttons of the paginator. See the ``buttons=`` kwarg on :class:`.ModalPaginator` for more information.


v0.0.1
-------

- Initial release!
