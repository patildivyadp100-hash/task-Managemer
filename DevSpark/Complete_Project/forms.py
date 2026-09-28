"""
=============================================================================
forms.py — Flask-WTF Web Form Validation (Module 14, 19)
=============================================================================
This file defines web forms using Flask-WTF and WTForms.

Why Flask-WTF?
  1. Automated Server-Side Validation: Guarantees title is not empty and fits length.
  2. CSRF (Cross-Site Request Forgery) Protection: Automatically injects hidden
     tokens in HTML forms to block malicious cross-origin requests.
  3. Clean Template Rendering: Fields handle their own labels, error lists,
     and pre-filled values.

Modules Covered:
  - Module 03: Object-Oriented Programming (Form inheritance from FlaskForm)
  - Module 14: Flask-WTF Forms, Fields, Validators, and CSRF Protection
  - Module 19: Separation of Form Logic from Views
=============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class AddTaskForm(FlaskForm):
    """
    Form for creating a new task from the web interface.
    New tasks default to 'pending' status.
    """
    title = StringField(
        "Task Title",
        validators=[
            DataRequired(message="Task title is required."),
            Length(min=3, max=100, message="Title must be between 3 and 100 characters.")
        ],
        render_kw={"placeholder": "e.g., Build REST API for TaskFlow"}
    )

    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=500, message="Description cannot exceed 500 characters.")],
        render_kw={"rows": 4, "placeholder": "Add detailed instructions, requirements, or notes..."}
    )

    user_id = SelectField(
        "Assign to User",
        coerce=int,
        validators=[Optional()]
    )

    submit = SubmitField("Create Task")


class EditTaskForm(FlaskForm):
    """
    Form for editing an existing task's title, description, status, and user assignment.
    """
    title = StringField(
        "Task Title",
        validators=[
            DataRequired(message="Task title is required."),
            Length(min=3, max=100, message="Title must be between 3 and 100 characters.")
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=500, message="Description cannot exceed 500 characters.")],
        render_kw={"rows": 4}
    )

    status = SelectField(
        "Status",
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed")
        ],
        validators=[DataRequired(message="Please select a valid status.")]
    )

    user_id = SelectField(
        "Assigned User",
        coerce=int,
        validators=[Optional()]
    )

    submit = SubmitField("Save Changes")
