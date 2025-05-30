// 🎯 Mini-Git Web Interface - JavaScript Application Modernizado
// Archivo principal del frontend: maneja la interacción con la API, el estado y la UI.

/**
 * Clase para interactuar con la API REST de Mini-Git.
 * Provee métodos para todas las operaciones del backend.
 */
class MiniGitAPI {
    /**
     * Inicializa la API con la URL base.
     */
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    /**
     * Realiza una petición HTTP a la API.
     */
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options
        });
        if (!response.ok) {
            let errorMsg = `HTTP error! status: ${response.status}`;
            try { const error = await response.json(); errorMsg = error.detail || errorMsg; } catch {}
            throw new Error(errorMsg);
        }
        return await response.json();
    }
    /** Inicializa el repositorio */
    async initRepository() { return this.request('/init', { method: 'POST' }); }
    /** Obtiene el estado del repositorio */
    async getStatus() { return this.request('/status'); }
    /** Agrega archivos y los añade al staging */
    async addFiles(files) { return this.request('/add', { method: 'POST', body: JSON.stringify(files) }); }
    /** Crea un commit con los archivos staged */
    async createCommit(message) { return this.request('/commit', { method: 'POST', body: JSON.stringify({ message }) }); }
    /** Obtiene el historial de commits */
    async getCommitHistory(limit = 10) { return this.request(`/log?limit=${limit}`); }
    /** Lista todos los archivos del repositorio */
    async listFiles() { return this.request('/files'); }
    /** Obtiene el contenido de un archivo */
    async getFileContent(filePath) { return this.request(`/file/${encodeURIComponent(filePath)}`); }
    /** Obtiene los detalles de un commit */
    async getCommitDetails(commitHash) { return this.request(`/commit/${commitHash}`); }
    /** Elimina un archivo del repositorio */
    async deleteFile(filePath) {
        return this.request(`/file/${encodeURIComponent(filePath)}`, { method: 'DELETE' });
    }
    /** Obtiene el diff de un archivo respecto al último commit */
    async getFileDiff(filePath) {
        return this.request(`/diff/${encodeURIComponent(filePath)}`);
    }
    /** Agrega un archivo al área de staging */
    async stageFile(filePath) {
        return this.request(`/stage/${encodeURIComponent(filePath)}`, { method: 'POST' });
    }
    /** Quita un archivo del área de staging */
    async unstageFile(filePath) {
        return this.request(`/unstage/${encodeURIComponent(filePath)}`, { method: 'POST' });
    }
}

/**
 * Clase para manejar el estado global de la aplicación.
 */
class AppState {
    constructor() {
        this.currentPage = 'dashboard';
        this.repository = null;
        this.commits = [];
        this.files = [];
        this.stagingFiles = [];
        this.isLoading = false;
        this.lastUpdate = null;
    }
    /** Actualiza el estado y notifica a los listeners */
    setState(newState) {
        Object.assign(this, newState);
        this.lastUpdate = new Date();
        this.notifyStateChange();
    }
    /** Dispara un evento global para notificar cambios de estado */
    notifyStateChange() {
        window.dispatchEvent(new CustomEvent('stateChange', { detail: this }));
    }
}

/**
 * Clase de utilidades para la UI: alertas, loading, formato de fechas, etc.
 */
class UIHelper {
    /** Muestra una alerta flotante */
    static showAlert(message, type = 'info', timeout = 5000) {
        const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                ${this.getAlertIcon(type)}
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="margin-left: auto; background: none; border: none; cursor: pointer; opacity: 0.7;">×</button>
            </div>
        `;
        alertContainer.appendChild(alert);
        setTimeout(() => { if (alert.parentNode) alert.remove(); }, timeout);
    }
    /** Crea el contenedor de alertas si no existe */
    static createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        document.body.appendChild(container);
        return container;
    }
    /** Devuelve el icono correspondiente al tipo de alerta */
    static getAlertIcon(type) {
        const icons = { success: '✓', error: '✗', warning: '⚠', info: 'ℹ' };
        return icons[type] || icons.info;
    }
    /** Formatea una fecha a string legible en español */
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    }
    /** Muestra u oculta un spinner de carga sobre un elemento */
    static setLoading(elementId, isLoading) {
        const element = document.getElementById(elementId);
        if (!element) return;
        if (isLoading) {
            element.style.opacity = '0.6';
            element.style.pointerEvents = 'none';
            if (!element.querySelector('.spinner')) {
                const spinner = document.createElement('div');
                spinner.className = 'loading';
                spinner.innerHTML = '<div class="spinner"></div><span>Cargando...</span>';
                element.appendChild(spinner);
            }
        } else {
            element.style.opacity = '1';
            element.style.pointerEvents = 'auto';
            const spinner = element.querySelector('.loading');
            if (spinner) spinner.remove();
        }
    }
}

/**
 * Clase principal que maneja la lógica de la página, interacción con la API y renderizado de la UI.
 */
class PageHandler {
    /** Inicializa con la API y el estado global */
    constructor(api, state) {
        this.api = api;
        this.state = state;
    }
    /** Carga y renderiza el dashboard (estado del repo) */
    async loadDashboard() {
        try {
            UIHelper.setLoading('dashboard', true);
            const status = await this.api.getStatus();
            this.state.setState({ repository: status });
            this.renderDashboard(status);
            if (status.initialized) await this.loadRecentCommits();
        } catch (error) {
            UIHelper.showAlert(`Error al cargar dashboard: ${error.message}`, 'error');
        } finally {
            UIHelper.setLoading('dashboard', false);
        }
    }
    /** Renderiza el dashboard con estadísticas y estado */
    renderDashboard(status) {
        const statsContainer = document.getElementById('repo-stats');
        if (!statsContainer) return;
        if (!status.initialized) {
            statsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📁</div>
                    <h3>Repositorio no inicializado</h3>
                    <p>Inicializa un repositorio para comenzar a usar Mini-Git</p>
                    <button class="btn btn-primary mt-3" id="init-btn-2">🚀 Inicializar Repositorio</button>
                </div>
            `;
            setTimeout(() => {
                const btn = document.getElementById('init-btn-2');
                if (btn) btn.onclick = () => window.pageHandler.initRepository();
            }, 100);
            return;
        }
        statsContainer.innerHTML = `
            <div class="status-grid">
                <div class="stat-card">
                    <div class="stat-number">${status.total_commits}</div>
                    <div class="stat-label">Commits</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${status.staged_files?.length || 0}</div>
                    <div class="stat-label">Archivos Staged</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${status.current_branch}</div>
                    <div class="stat-label">Branch Actual</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${status.clean ? '✓' : '!'}</div>
                    <div class="stat-label">Estado</div>
                </div>
            </div>
            <div class="card">
                <h3>Estado del Repositorio</h3>
                <p><strong>Directorio:</strong> ${status.working_directory}</p>
                <p><strong>Branch:</strong> ${status.current_branch}</p>
                <p><strong>Estado:</strong> ${status.clean ? 'Limpio' : 'Cambios pendientes'}</p>
            </div>
        `;
    }
    /** Carga y renderiza los commits recientes */
    async loadRecentCommits() {
        try {
            const commits = await this.api.getCommitHistory(5);
            this.renderRecentCommits(commits);
        } catch (error) {
            console.error('Error loading recent commits:', error);
        }
    }
    /** Renderiza la lista de commits recientes */
    renderRecentCommits(commits) {
        const container = document.getElementById('commit-history');
        if (!container) return;
        if (commits.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <h3>Sin commits aún</h3>
                    <p>Crea tu primer commit para ver el historial</p>
                </div>
            `;
            return;
        }
        container.innerHTML = `
            <h3>Commits Recientes</h3>
            <div class="commit-list">
                ${commits.map(commit => `
                    <div class="commit-item" onclick="window.pageHandler.showCommitDetails('${commit.hash}')">
                        <div class="commit-hash">${commit.hash.substring(0, 8)}</div>
                        <div class="commit-message">${commit.message}</div>
                        <div class="commit-meta">
                            <div class="commit-author">${commit.author}</div>
                            <div class="commit-date">${UIHelper.formatDate(commit.timestamp)}</div>
                            <div class="commit-files">${commit.files_count || 0} archivos</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    /** Carga y renderiza la lista de archivos, separando staged y no staged */
    async loadFiles() {
        try {
            UIHelper.setLoading('files', true);
            const status = await this.api.getStatus();
            const response = await this.api.listFiles();
            // Guardar staged_files en el estado
            this.state.setState({ files: response.files || [], stagedFiles: status.staged_files || [] });
            this.renderFiles(response.files || [], status.staged_files || []);
        } catch (error) {
            UIHelper.showAlert(`Error al cargar archivos: ${error.message}`, 'error');
        } finally {
            UIHelper.setLoading('files', false);
        }
    }
    /** Renderiza los archivos, mostrando botones para staging/unstaging/diff/eliminar */
    renderFiles(files, stagedFiles = []) {
        const container = document.getElementById('file-list');
        if (!container) return;
        if (files.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📄</div>
                    <h3>Sin archivos</h3>
                    <p>Añade archivos al repositorio para verlos aquí</p>
                </div>
            `;
            return;
        }
        // Separar archivos staged y no staged
        const staged = files.filter(f => stagedFiles.includes(f));
        const notStaged = files.filter(f => !stagedFiles.includes(f));
        container.innerHTML = `
            <div class="file-explorer">
                <h4 style="margin-bottom:0.3em;">Staged</h4>
                ${staged.length === 0 ? '<div style="color:#888;">(Vacío)</div>' : ''}
                ${staged.map(file => `
                    <div class="file-item">
                        <div class="file-icon">📄</div>
                        <div class="file-name" onclick="window.pageHandler.selectFile('${file}')">${file}</div>
                        <button class="btn btn-warning" title="Quitar del staging" onclick="window.pageHandler.unstageFile(event, '${file}')">- Quitar</button>
                        <button class="btn btn-secondary" title="Ver Diff" onclick="window.pageHandler.showFileDiff(event, '${file}')">📝 Diff</button>
                        <button class="btn btn-error" title="Eliminar archivo" style="margin-left:auto;" onclick="window.pageHandler.deleteFile(event, '${file}')">🗑️</button>
                    </div>
                `).join('')}
                <h4 style="margin:1em 0 0.3em 0;">No staged</h4>
                ${notStaged.length === 0 ? '<div style="color:#888;">(Vacío)</div>' : ''}
                ${notStaged.map(file => `
                    <div class="file-item">
                        <div class="file-icon">📄</div>
                        <div class="file-name" onclick="window.pageHandler.selectFile('${file}')">${file}</div>
                        <button class="btn btn-success" title="Agregar al staging" onclick="window.pageHandler.stageFile(event, '${file}')">+ Staging</button>
                        <button class="btn btn-secondary" title="Ver Diff" onclick="window.pageHandler.showFileDiff(event, '${file}')">📝 Diff</button>
                        <button class="btn btn-error" title="Eliminar archivo" style="margin-left:auto;" onclick="window.pageHandler.deleteFile(event, '${file}')">🗑️</button>
                    </div>
                `).join('')}
            </div>
        `;
    }
    /** Carga y renderiza el historial completo de commits */
    async loadCommits() {
        try {
            UIHelper.setLoading('commits', true);
            const commits = await this.api.getCommitHistory(20);
            this.state.setState({ commits });
            this.renderCommits(commits);
        } catch (error) {
            UIHelper.showAlert(`Error al cargar commits: ${error.message}`, 'error');
        } finally {
            UIHelper.setLoading('commits', false);
        }
    }
    /** Renderiza la lista de commits */
    renderCommits(commits) {
        const container = document.getElementById('commit-history');
        if (!container) return;
        if (commits.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🕐</div>
                    <h3>Sin historial</h3>
                    <p>El historial de commits aparecerá aquí</p>
                </div>
            `;
            return;
        }
        container.innerHTML = `
            <div class="commit-list">
                ${commits.map(commit => `
                    <div class="commit-item" onclick="window.pageHandler.showCommitDetails('${commit.hash}')">
                        <div class="commit-hash">${commit.hash.substring(0, 8)}</div>
                        <div class="commit-message">${commit.message}</div>
                        <div class="commit-meta">
                            <div class="commit-author">${commit.author}</div>
                            <div class="commit-date">${UIHelper.formatDate(commit.timestamp)}</div>
                            <div class="commit-files">${commit.files_count || 0} archivos</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    /** Inicializa el repositorio desde la UI */
    async initRepository() {
        UIHelper.showAlert('Inicializando repositorio...', 'info');
        try {
            await this.api.initRepository();
            UIHelper.showAlert('Repositorio inicializado con éxito', 'success');
            await this.loadDashboard();
            await this.loadFiles();
        } catch (err) {
            UIHelper.showAlert(`Error al inicializar repositorio: ${err.message}`, 'error');
        }
    }
    /** Muestra el contenido de un archivo en un modal */
    async selectFile(filePath) {
        try {
            const file = await this.api.getFileContent(filePath);
            const fileContentPanel = document.getElementById('file-content-modal');
            fileContentPanel.querySelector('.modal-title').innerText = filePath;
            fileContentPanel.querySelector('.modal-body').innerText = file.content || '';
            fileContentPanel.style.display = 'block';
        } catch (err) {
            UIHelper.showAlert('Error al cargar archivo: ' + err.message, 'error');
        }
    }
    /** Muestra los detalles de un commit en un modal */
    async showCommitDetails(commitHash) {
        try {
            const commit = await this.api.getCommitDetails(commitHash);
            const commitDetailModal = document.getElementById('commit-detail-modal');
            commitDetailModal.querySelector('.modal-title').innerText = `Commit ${commit.hash.substring(0, 8)}`;
            commitDetailModal.querySelector('.modal-body').innerHTML = `
                <p><strong>Mensaje:</strong> ${commit.message}</p>
                <p><strong>Autor:</strong> ${commit.author}</p>
                <p><strong>Fecha:</strong> ${UIHelper.formatDate(commit.timestamp)}</p>
                <p><strong>Archivos afectados:</strong></p>
                <ul>${commit.files.map(file => `<li>${file}</li>`).join('')}</ul>
            `;
            commitDetailModal.style.display = 'block';
        } catch (err) {
            UIHelper.showAlert('Error al cargar detalles del commit: ' + err.message, 'error');
        }
    }
    /** Agrega un archivo al repositorio y lo añade al staging */
    async addFile(fileName, fileContent) {
        try {
            await this.api.addFiles([{ name: fileName, content: fileContent }]);
            UIHelper.showAlert('Archivo añadido', 'success');
            await this.loadFiles();
            await this.loadDashboard();
        } catch (err) {
            UIHelper.showAlert('Error al agregar archivo: ' + err.message, 'error');
        }
    }
    /** Realiza un commit con los archivos staged */
    async commitChanges(commitMessage) {
        try {
            await this.api.createCommit(commitMessage);
            UIHelper.showAlert('Commit realizado', 'success');
            await this.loadDashboard();
            await this.loadRecentCommits();
        } catch (err) {
            UIHelper.showAlert('Error al hacer commit: ' + err.message, 'error');
        }
    }
    /** Elimina un archivo del repositorio y del staging */
    async deleteFile(event, filePath) {
        event.stopPropagation();
        if (!confirm(`¿Seguro que deseas eliminar '${filePath}'?`)) return;
        try {
            await this.api.deleteFile(filePath);
            UIHelper.showAlert('Archivo eliminado', 'success');
            await this.loadFiles();
            await this.loadDashboard();
        } catch (err) {
            UIHelper.showAlert('Error al eliminar archivo: ' + err.message, 'error');
        }
    }
    /** Muestra el diff de un archivo en un modal */
    async showFileDiff(event, filePath) {
        event.stopPropagation();
        try {
            const result = await this.api.getFileDiff(filePath);
            let diff = result.diff || '';
            if (!diff) diff = '(Sin diferencias o archivo nuevo)';
            let modal = document.getElementById('diff-modal');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'diff-modal';
                modal.className = 'modal';
                modal.innerHTML = `
                    <div class="modal-content">
                        <span class="close" onclick="document.getElementById('diff-modal').style.display='none'">&times;</span>
                        <h3 class="modal-title">Diff</h3>
                        <pre class="modal-body" style="background:#222;color:#fff;padding:1em;border-radius:8px;max-height:400px;overflow:auto;font-size:0.95em;"></pre>
                    </div>
                `;
                document.body.appendChild(modal);
            }
            modal.querySelector('.modal-title').innerText = `Diff: ${filePath}`;
            modal.querySelector('.modal-body').innerText = diff;
            modal.style.display = 'block';
        } catch (err) {
            UIHelper.showAlert('Error al obtener diff: ' + err.message, 'error');
        }
    }
    /** Agrega un archivo al área de staging desde la UI */
    async stageFile(event, filePath) {
        event.stopPropagation();
        try {
            await this.api.stageFile(filePath);
            UIHelper.showAlert('Archivo añadido al staging', 'success');
            await this.loadFiles();
            await this.loadDashboard();
        } catch (err) {
            UIHelper.showAlert('Error al añadir al staging: ' + err.message, 'error');
        }
    }
    /** Quita un archivo del área de staging desde la UI */
    async unstageFile(event, filePath) {
        event.stopPropagation();
        try {
            await this.api.unstageFile(filePath);
            UIHelper.showAlert('Archivo quitado del staging', 'success');
            await this.loadFiles();
            await this.loadDashboard();
        } catch (err) {
            UIHelper.showAlert('Error al quitar del staging: ' + err.message, 'error');
        }
    }
}

// ===================== INICIALIZACIÓN GLOBAL =====================
// Configura la app y los listeners de formularios y modales
window.addEventListener('DOMContentLoaded', () => {
    window.miniGitApi = new MiniGitAPI();
    window.appState = new AppState();
    window.pageHandler = new PageHandler(window.miniGitApi, window.appState);
    window.pageHandler.loadDashboard();
    window.pageHandler.loadFiles();

    // Formularios y botones principales
    document.getElementById('init-btn').onclick = () => window.pageHandler.initRepository();
    document.getElementById('add-file-form').onsubmit = function(e) {
        e.preventDefault();
        const fileName = document.getElementById('file-name').value;
        const fileContent = document.getElementById('file-content-input').value;
        window.pageHandler.addFile(fileName, fileContent);
        this.reset();
    };
    document.getElementById('commit-form').onsubmit = function(e) {
        e.preventDefault();
        const commitMessage = document.getElementById('commit-message').value;
        window.pageHandler.commitChanges(commitMessage);
        this.reset();
    };
    // Cerrar modales de detalles
    document.getElementById('file-content-modal').addEventListener('click', (event) => {
        if (event.target.classList.contains('close')) {
            document.getElementById('file-content-modal').style.display = 'none';
        }
    });
    document.getElementById('commit-detail-modal').addEventListener('click', (event) => {
        if (event.target.classList.contains('close')) {
            document.getElementById('commit-detail-modal').style.display = 'none';
        }
    });
});
// ===================== FIN DEL ARCHIVO PRINCIPAL =====================
