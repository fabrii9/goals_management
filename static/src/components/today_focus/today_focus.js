/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { Component, useState } from "@odoo/owl";

export class GoalsTodayFocus extends Component {
    static template = "goals_management.TodayFocus";
    static props = {
        focusList: { type: Array, optional: true },
        onChange: { type: Function, optional: true },
    };
    static defaultProps = {
        focusList: [],
    };

    setup() {
        this.state = useState({
            focusList: this.props.focusList,
            loading: {},
        });
    }

    async toggleFocus(focus) {
        if (this.state.loading[focus.id]) {
            return;
        }
        this.state.loading[focus.id] = true;
        const newState = focus.state === "done" ? "pending" : "done";
        try {
            await rpc("/web/dataset/call_kw/goals.daily.focus/write", {
                model: "goals.daily.focus",
                method: "write",
                args: [[focus.id], { state: newState }],
                kwargs: {},
            });
            focus.state = newState;
            if (this.props.onChange) {
                this.props.onChange();
            }
        } finally {
            this.state.loading[focus.id] = false;
        }
    }

    getStateClass(focus) {
        return focus.state === "done"
            ? "o_goals_focus_done text-decoration-line-through text-muted"
            : "o_goals_focus_pending";
    }
}
