/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Widget Organigramme pour le back-office Odoo
 * Utilise OrgChart.js pour afficher la hiérarchie interactive
 */
export class OrgChartWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            error: null,
            data: null,
        });

        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            if (this.state.data) {
                this.renderOrgChart();
            }
        });
    }

    /**
     * Charger les données hiérarchiques depuis Odoo
     */
    async loadData() {
        try {
            const ministryId = this.props.ministry_id || null;
            
            // Appel RPC pour récupérer les données
            const result = await this.orm.call(
                "sn.ministry",
                "get_orgchart_data",
                [ministryId],
                {}
            );
            
            this.state.data = result;
            this.state.loading = false;
        } catch (error) {
            console.error("Erreur lors du chargement de l'organigramme:", error);
            this.state.error = "Impossible de charger l'organigramme";
            this.state.loading = false;
        }
    }

    /**
     * Afficher l'organigramme avec OrgChart.js
     */
    renderOrgChart() {
        const container = this.el.querySelector("#orgchart-container");
        if (!container || !this.state.data) return;

        // Vérifier si OrgChart.js est chargé
        if (typeof $ === 'undefined' || typeof $.fn.orgchart === 'undefined') {
            console.error("OrgChart.js n'est pas chargé");
            this.state.error = "Bibliothèque OrgChart.js manquante";
            return;
        }

        // Configuration OrgChart.js
        $(container).orgchart({
            data: this.state.data,
            nodeContent: 'title',
            pan: true,
            zoom: true,
            depth: 3,
            exportButton: true,
            exportFilename: 'organigramme_senegal',
            nodeTemplate: this.getNodeTemplate.bind(this),
        });

        // Gérer les clics sur les nœuds
        $(container).on('click', '.node', (event) => {
            const nodeId = $(event.currentTarget).data('node-id');
            const nodeType = $(event.currentTarget).data('node-type');
            this.openNodeRecord(nodeType, nodeId);
        });
    }

    /**
     * Template HTML pour chaque nœud
     */
    getNodeTemplate(data) {
        const typeColors = {
            'presidency': '#E31B23',
            'primature': '#0066CC',
            'ministry': '#00853F',
            'direction': '#FDEF42',
            'service': '#CCCCCC',
            'agent': '#FFFFFF',
        };

        const typeIcons = {
            'presidency': 'fa-landmark',
            'primature': 'fa-building',
            'ministry': 'fa-building',
            'direction': 'fa-sitemap',
            'service': 'fa-briefcase',
            'agent': 'fa-user',
        };

        const bgColor = typeColors[data.type] || '#FFFFFF';
        const icon = typeIcons[data.type] || 'fa-circle';
        const textColor = ['presidency', 'primature', 'ministry'].includes(data.type) ? '#FFFFFF' : '#212529';

        return `
            <div class="node-card" style="background-color: ${bgColor}; color: ${textColor};" 
                 data-node-id="${data.id}" data-node-type="${data.model}">
                <div class="node-icon">
                    <i class="fa ${icon}"></i>
                </div>
                <div class="node-title">${data.name}</div>
                <div class="node-subtitle">${data.code || ''}</div>
                ${data.children_count ? `<div class="node-count">${data.children_count} sous-structures</div>` : ''}
            </div>
        `;
    }

    /**
     * Ouvrir la fiche Odoo correspondante
     */
    openNodeRecord(model, id) {
        if (!model || !id) return;

        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: model,
            res_id: id,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    /**
     * Rafraîchir l'organigramme
     */
    async refresh() {
        this.state.loading = true;
        await this.loadData();
        if (this.state.data) {
            this.renderOrgChart();
        }
    }

    /**
     * Exporter l'organigramme en PNG
     */
    exportPNG() {
        const container = this.el.querySelector("#orgchart-container");
        if (container && typeof $.fn.orgchart !== 'undefined') {
            $(container).orgchart('export', 'organigramme_senegal.png');
        }
    }

    /**
     * Exporter l'organigramme en PDF
     */
    exportPDF() {
        const container = this.el.querySelector("#orgchart-container");
        if (container && typeof $.fn.orgchart !== 'undefined') {
            $(container).orgchart('export', 'organigramme_senegal.pdf');
        }
    }

    /**
     * Plein écran
     */
    toggleFullscreen() {
        const container = this.el.querySelector("#orgchart-container");
        if (!container) return;

        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => {
                console.error("Erreur plein écran:", err);
            });
        } else {
            document.exitFullscreen();
        }
    }
}

OrgChartWidget.template = "sn_admin.OrgChartWidget";

// Enregistrer le widget
registry.category("fields").add("sn_orgchart", OrgChartWidget);

export default OrgChartWidget;
