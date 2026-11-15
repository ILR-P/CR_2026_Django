from django import forms


class SimulationActionForm(forms.Form):
    """Controls posted from /simulate."""

    RESET = "reset"
    LOAD_FIGHTS = "load_fights"

    action = forms.ChoiceField(choices=[
        (RESET, "Reset health & replay all fights"),
        (LOAD_FIGHTS, "Load fights from host"),
    ])
    host = forms.URLField(
        required=False,
        label="Fight host URL",
        help_text="Only needed for 'Load fights from host'.",
        widget=forms.TextInput(attrs={"placeholder": "https://…"}),
    )
