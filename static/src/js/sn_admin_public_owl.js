/** @odoo-module **/

// Minimal JSON-RPC helper using fetch, suitable for website context
async function jsonRpc(url, params = {}) {
    const payload = {
        jsonrpc: '2.0',
        method: 'call',
        params,
    };
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'same-origin',
    });
    const data = await res.json();
    if (data && Object.prototype.hasOwnProperty.call(data, 'result')) {
        return data.result;
    }
    throw new Error('Invalid JSON-RPC response');
}

function nodeUrlForModel(model, id) {
    switch (model) {
        case 'sn.ministry':
            return `/organigramme/ministere/${id}`;
        case 'sn.category':
            return `/organigramme/categorie/${id}`;
        case 'sn.direction':
            return `/organigramme/direction/${id}`;
        case 'sn.service':
            return `/organigramme/service/${id}`;
        case 'sn.agent':
            return `/organigramme/agent/${id}`;
        default:
            return '#';
    }
}

function renderTree(container, data) {
    container.innerHTML = '';
    const root = buildTreeElement(data);
    container.appendChild(root);
}

function buildTreeElement(node) {
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

    title.prepend(name);

    title.addEventListener('click', () => {
        if (node.model && node.id) {
            const url = nodeUrlForModel(node.model, node.id);
            if (url !== '#') {
                window.location.href = url;
            }
        }
    });

    li.appendChild(title);

    if (Array.isArray(node.children) && node.children.length) {
        const childrenUl = document.createElement('ul');
        childrenUl.className = 'sn-org-children list-unstyled ps-3 ms-2 border-start';
        for (const child of node.children) {
            const childTree = buildTreeElement(child);
            childrenUl.appendChild(childTree.firstChild);
        }
        li.appendChild(childrenUl);
    }

    ul.appendChild(li);
    return ul;
}

async function initPublicOrgChart() {
    const container = document.getElementById('orgchart-container');
    if (!container) return;

    // loader
    container.innerHTML = '<div class="d-flex justify-content-center align-items-center py-5"><div class="spinner-border" role="status"><span class="visually-hidden">Chargement...</span></div></div>';

    try {
        const ministryIdAttr = container.getAttribute('data-ministry-id');
        const ministry_id = ministryIdAttr ? parseInt(ministryIdAttr, 10) : undefined;
        const result = await jsonRpc('/organigramme/api/tree', { ministry_id });
        renderTree(container, result);
    } catch (err) {
        // error display
        container.innerHTML = '<div class="alert alert-danger"><i class="fa fa-exclamation-triangle me-2"></i>Erreur lors du chargement de l\'organigramme</div>';
        // eslint-disable-next-line no-console
        console.error('OrgChart load error:', err);
    }
}

// Auto-init on ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPublicOrgChart);
} else {
    initPublicOrgChart();
}

export default {
    initPublicOrgChart,
};
