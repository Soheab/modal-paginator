.. currentmodule:: discord.ext.modal_paginator

Custom Buttons
===============
The extension provides a way to customise the buttons used in the paginator.

.. autoclass:: CustomButton
    :members:
    :show-inheritance:

.. currentmodule:: discord.ext.modal_paginator.default_buttons

Default Buttons
++++++++++++++++
See here the default buttons used in the paginator. These are for reference only, and should not be used directly.

OpenButton
-----------
.. autoclass:: OpenButton
    :show-inheritance:
.. automethod:: discord.ext.modal_paginator.default_buttons.OpenButton.on_required_modal
.. automethod:: discord.ext.modal_paginator.default_buttons.OpenButton.on_optional_modal

NextButton
-----------
.. autoclass:: NextButton
    :show-inheritance:

PreviousButton
---------------
.. autoclass:: PreviousButton
    :show-inheritance:

CancelButton
------------
.. autoclass:: CancelButton
    :show-inheritance:

FinishButton
-------------
.. autoclass:: FinishButton
    :show-inheritance: