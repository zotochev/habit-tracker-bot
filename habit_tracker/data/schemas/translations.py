from pydantic import BaseModel


class Translations(BaseModel):
    start: str = '<START>'
    choose_language: str = '<CHOOSE_LANGUAGE>'
    language_chosen: str = '<LANGUAGE_CHOSEN>'
    create_habit: str = '<CREATE_HABIT>'
    button_create_habit: str = '<BUTTON_CREATE_HABIT>'
    enter_habit_name: str = '<ENTER_HABIT_NAME>'
    wrong_type_habit_name: str = '<WRONG_TYPE_HABIT_NAME>'
    habit_name_too_long: str = '<HABIT_NAME_TOO_LONG>'
    enter_habit_description: str = '<ENTER_HABIT_DESCRIPTION>'
    wrong_type_habit_description: str = '<WRONG_TYPE_HABIT_DESCRIPTION>'
    habit_description_too_long: str = '<HABIT_DESCRIPTION_TOO_LONG>'
    enter_habit_start_date: str = '<ENTER_HABIT_START_DATE>'
