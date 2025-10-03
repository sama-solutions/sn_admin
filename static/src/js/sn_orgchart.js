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

        // Rendu DOM simple (OWL natif, sans jQuery)
        container.innerHTML = '';
        const tree = this._buildTreeElement(this.state.data);
        container.appendChild(tree);
    }

    _buildTreeElement(node) {
        const ul = document.createElement('ul');
        ul.className = 'sn-org-ul list-unstyled';

        const li = document.createElement('li');
        li.className = 'sn-org-li mb-2';

        const title = document.createElement('div');
        title.className = 'sn-org-node d-flex align-items-center gap-2';
        title.style.cursor = 'pointer';

        const name = document.createElement('span');
        name.textContent = node.name || '';
        name.className = 'fw-semibold';
        title.appendChild(name);

        if (node.title) {
            const badge = document.createElement('span');
            badge.textContent = node.title;
            badge.className = 'badge text-bg-secondary';
            title.appendChild(badge);
        }

        if (node.children_count) {
            const count = document.createElement('span');
            count.textContent = `${node.children_count}`;
            count.className = 'badge text-bg-info';
            title.appendChild(count);
        }

        title.addEventListener('click', () => {
            if (node.model && node.id) {
                this.openNodeRecord(node.model, node.id);
            }
        });

        li.appendChild(title);

        if (Array.isArray(node.children) && node.children.length) {
            const childrenUl = document.createElement('ul');
            childrenUl.className = 'sn-org-children list-unstyled ps-3 ms-2 border-start';
            for (const child of node.children) {
                const childTree = this._buildTreeElement(child);
                childrenUl.appendChild(childTree.firstChild);
            }
            li.appendChild(childrenUl);
        }

        ul.appendChild(li);
        return ul;
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
        // Fallback sans dépendance: utiliser la fonction d'impression du navigateur
        window.print();
    }

    /**
     * Exporter l'organigramme en PDF
     */
    exportPDF() {
        // Fallback sans dépendance: utiliser la fonction d'impression du navigateur
        window.print();
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
