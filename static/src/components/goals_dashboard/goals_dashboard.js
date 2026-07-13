/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component, useState, onWillStart } from "@odoo/owl";
import { GoalsProgressBar } from "@goals_management/components/progress_bar/progress_bar";
import { GoalsTodayFocus } from "@goals_management/components/today_focus/today_focus";

export class GoalsDashboard extends Component {
    static template = "goals_management.Dashboard";
    static components = { Layout, GoalsProgressBar, GoalsTodayFocus };
    static props = ["*"];

    setup() {
        this.state = useState({
            data: null,
            loading: true,
        });

        onWillStart(async () => {
            await this.fetchData();
        });
    }

    get display() {
        return {
            controlPanel: {},
        };
    }

    async fetchData() {
        this.state.loading = true;
        try {
            this.state.data = await rpc("/goals/dashboard/data");
        } finally {
            this.state.loading = false;
        }
    }

    get yearProgress() {
        return this.state.data?.year_goal?.progress || 0;
    }

    get weekProgress() {
        return this.state.data?.week_goal?.progress || 0;
    }

    get user() {
        return this.state.data?.user || {};
    }

    get hasGamification() {
        return this.state.data?.gamification_enabled;
    }

    get productivityChart() {
        const data = this.state.data?.productivity_data || [];
        const max = Math.max(...data.map((d) => d.completed), 1);
        return data.map((d) => ({
            ...d,
            height: Math.round((d.completed / max) * 100),
            label: new Date(d.date).toLocaleDateString("es-ES", {
                weekday: "short",
            }),
        }));
    }
}

registry.category("actions").add("goals.dashboard", GoalsDashboard);
