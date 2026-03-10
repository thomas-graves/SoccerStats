/**
 * Admin helper for MatchEventQualifier forms.
 *
 * This script improves qualifier entry by switching the text_value input
 * between:
 * - a normal text box for uncontrolled text qualifiers
 * - a dropdown for controlled text qualifiers
 *
 * It is designed to work for:
 * - the standalone MatchEventQualifier admin form
 * - qualifier inline rows inside the MatchEvent admin form
 *
 * Note:
 * This script only handles the UI layer. Model validation still remains the
 * source of truth for correctness.
 */
(function () {
    "use strict";

    /**
     * Controlled text vocabularies for qualifier keys.
     *
     * These should stay aligned with QUALIFIER_ALLOWED_TEXT_VALUES
     * in events/models.py.
     */
    const QUALIFIER_ALLOWED_TEXT_VALUES = {
        body_part: ["chest", "hands", "head", "left_foot", "other", "right_foot"],
        pass_length: ["long", "medium", "short"],
        pass_profile: ["cross", "cutback", "long_ball", "long_pass", "switch", "through_ball"],
        pass_height: ["ground", "lofted"],
        pass_direction: ["backward", "forward", "lateral"],
        restart_type: ["corner", "free_kick", "goal_kick", "penalty", "throw_in"],
        restart_side: ["centre", "left", "right"],
        free_kick_profile: ["direct", "indirect"],
        subbed_on_position: [
            "CAM", "CB", "CDM", "CF", "CM", "GK", "LB", "LM", "LS",
            "LW", "LWB", "RB", "RM", "RS", "RW", "RWB", "ST"
        ],
        subbed_off_position: [
            "CAM", "CB", "CDM", "CF", "CM", "GK", "LB", "LM", "LS",
            "LW", "LWB", "RB", "RM", "RS", "RW", "RWB", "ST"
        ],
        position_from: [
            "CAM", "CB", "CDM", "CF", "CM", "GK", "LB", "LM", "LS",
            "LW", "LWB", "RB", "RM", "RS", "RW", "RWB", "ST"
        ],
        position_to: [
            "CAM", "CB", "CDM", "CF", "CM", "GK", "LB", "LM", "LS",
            "LW", "LWB", "RB", "RM", "RS", "RW", "RWB", "ST"
        ],
        shot_zone: ["inside_box", "outside_box"],
        shot_target_horizontal: ["centre", "left", "right"],
        shot_target_vertical: ["high", "low", "mid"],
        tackle_profile: ["sliding", "standing"],
        foul_profile: [
            "biting",
            "charging",
            "dangerous_play",
            "goalkeeping_offence",
            "handling",
            "holding",
            "kicking",
            "pushing",
            "spitting",
            "striking",
            "tackling",
            "tripping"
        ],
        card_type: ["red", "second_yellow_red", "yellow"]
    };

    /**
     * Build a select element for a controlled text qualifier.
     *
     * The new select preserves the original element's:
     * - name
     * - id
     * - class list
     * - current value where possible
     */
    function buildSelectFromInput(inputElement, allowedValues) {
        const selectElement = document.createElement("select");

        selectElement.name = inputElement.name;
        selectElement.id = inputElement.id;
        selectElement.className = inputElement.className;

        // Add the blank option used by Django admin fields.
        const blankOption = document.createElement("option");
        blankOption.value = "";
        blankOption.textContent = "---------";
        selectElement.appendChild(blankOption);

        // Add the controlled qualifier values.
        allowedValues.forEach(function (value) {
            const optionElement = document.createElement("option");
            optionElement.value = value;
            optionElement.textContent = value;
            selectElement.appendChild(optionElement);
        });

        // Preserve the current value where possible.
        if (allowedValues.includes(inputElement.value)) {
            selectElement.value = inputElement.value;
        }

        return selectElement;
    }

    /**
     * Build a plain text input from an existing select element.
     *
     * This is used when the admin changes from a controlled text qualifier
     * back to one that should use free text.
     */
    function buildInputFromSelect(selectElement) {
        const inputElement = document.createElement("input");

        inputElement.type = "text";
        inputElement.name = selectElement.name;
        inputElement.id = selectElement.id;
        inputElement.className = selectElement.className;
        inputElement.value = selectElement.value || "";

        return inputElement;
    }

    /**
     * For a given qualifier key field, locate the matching text_value field
     * in the same form container or inline row, then swap it to the correct
     * UI control if needed.
     */
    function updateTextValueWidgetForKeyField(keyField) {
        const fieldName = keyField.name;
        if (!fieldName) {
            return;
        }

        // Match Django admin field naming patterns such as:
        // qualifiers-0-key -> qualifiers-0-text_value
        // text_value on the standalone form remains just text_value.
        const textValueFieldName = fieldName.endsWith("-key")
            ? fieldName.replace(/-key$/, "-text_value")
            : "text_value";

        // Try to scope the lookup to the closest inline row or field/form container first.
        // This avoids accidentally finding the wrong text_value field elsewhere on the page.
        const container =
            keyField.closest("tr") ||
            keyField.closest(".inline-related") ||
            keyField.closest(".form-row") ||
            keyField.closest("fieldset") ||
            keyField.form ||
            document;

        let textValueField = container.querySelector(`[name="${textValueFieldName}"]`);

        // Fallback to a document-wide lookup if the scoped lookup fails.
        if (!textValueField) {
            textValueField = document.querySelector(`[name="${textValueFieldName}"]`);
        }

        if (!textValueField) {
            return;
        }

        const selectedKey = keyField.value;
        const allowedValues = QUALIFIER_ALLOWED_TEXT_VALUES[selectedKey];

        // Controlled text qualifier: switch to a dropdown if needed.
        if (allowedValues) {
            if (textValueField.tagName.toLowerCase() === "select") {
                // Refresh options if the key changed from one controlled key to another.
                const replacementSelect = buildSelectFromInput(
                    buildInputFromSelect(textValueField),
                    allowedValues
                );
                textValueField.replaceWith(replacementSelect);
            } else {
                const replacementSelect = buildSelectFromInput(textValueField, allowedValues);
                textValueField.replaceWith(replacementSelect);
            }
            return;
        }

        // Uncontrolled qualifier: ensure the field is a plain text input.
        if (textValueField.tagName.toLowerCase() === "select") {
            const replacementInput = buildInputFromSelect(textValueField);
            textValueField.replaceWith(replacementInput);
        }
    }

    /**
     * Apply the correct widget to any qualifier key fields already on the page.
     *
     * This is still useful on initial page load, but we no longer rely on
     * per-field event binding for dynamic inline rows.
     */
    function bindQualifierKeyFields() {
        const keyFields = document.querySelectorAll(
            'select[name="key"], select[name$="-key"]'
        );

        keyFields.forEach(function (keyField) {
            updateTextValueWidgetForKeyField(keyField);
        });
    }

    /**
     * Use event delegation so dynamically added inline rows also work.
     *
     * This is more reliable than binding change listeners directly to each
     * qualifier key field, because Django admin can add inline rows after
     * the initial page load.
     */
    function watchForInlineChanges() {
        document.addEventListener("change", function (event) {
            const target = event.target;

            if (
                target &&
                target.matches &&
                target.matches('select[name="key"], select[name$="-key"]')
            ) {
                updateTextValueWidgetForKeyField(target);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        bindQualifierKeyFields();
        watchForInlineChanges();
    });
})();

