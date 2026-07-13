/** @odoo-module **/

import { Component } from "@odoo/owl";

export class GoalsProgressBar extends Component {
    static template = "goals_management.ProgressBar";
    static props = {
        value: { type: Number, optional: true },
        max: { type: Number, optional: true },
        label: { type: String, optional: true },
        size: { type: String, optional: true },
    };
    static defaultProps = {
        value: 0,
        max: 100,
        size: "md",
    };

    get percentage() {
        const max = this.props.max || 100;
        const value = Math.min(Math.max(this.props.value || 0, 0), max);
        return max ? Math.round((value / max) * 100) : 0;
    }

    get heightClass() {
        const sizes = {
            sm: "o_goals_progress_sm",
            md: "o_goals_progress_md",
            lg: "o_goals_progress_lg",
        };
        return sizes[this.props.size] || sizes.md;
    }
}
