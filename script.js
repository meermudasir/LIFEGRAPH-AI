/**
 * =============================================================================
 * LifeGraph AI – Connected Intelligence Platform
 * Enterprise Graph & Vector Analytics Controller (Phase 3)
 * Inspired by Amazon Neptune Analytics
 * =============================================================================
 *
 * Architecture:
 * - LifeGraphConfig: Central platform configuration and endpoints
 * - LifeGraphState: Reactive application state
 * - LifeGraphData: Comprehensive sample graph & vector demo dataset
 * - LifeGraphAPI: Service client ready for Python FastAPI / Neo4j backend
 * - GraphVisualizer: Cytoscape.js interactive graph manager + fallback
 * - QueryConsoleManager: Gremlin / SPARQL / Cypher query simulator & executor
 * - KHopExplorerManager: K-Hop graph neighborhood traversal engine
 * - VectorSearchManager: High-dimensional semantic similarity engine
 * - AIIntelligenceManager: Autonomous graph ML & pattern discovery demo
 * - AnalyticsManager: Chart.js telemetry & activity monitoring
 * - UIController: Navigation, toasts, notifications, shortcuts, modals
 */

(() => {
  'use strict';

  /* ===========================================================================
   * 1. CONFIGURATION & CONSTANTS
   * =========================================================================== */
  const LifeGraphConfig = {
    appName: 'LifeGraph AI',
    version: '2.4 Enterprise',
    environment: 'us-east-neptune-prod',
    // Future FastAPI & Graph Backend Endpoints:
    apiBaseUrl: 'http://127.0.0.1:8000/api/v1',
    endpoints: {
      health: '/health',
      graphQuery: '/graph/query',
      vectorSearch: '/vector/search',
      khopTraversal: '/graph/khop',
      aiMetrics: '/ai/insights',
      systemTelemetry: '/analytics/telemetry'
    },
    // CDN Dependencies
    cytoscapeCdn: 'https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js',
    chartJsCdn: 'https://cdn.jsdelivr.net/npm/chart.js',
    // Visual Colors matching CSS variables in style.css
    colors: {
      bgMain: '#080D18',
      bgSidebar: '#0C1422',
      bgPanel: '#111C2D',
      bgPanelSecondary: '#152238',
      cyan: '#22D3EE',
      blue: '#3B82F6',
      purple: '#A855F7',
      success: '#22C55E',
      warning: '#F59E0B',
      danger: '#EF4444',
      person: '#38BDF8',
      org: '#818CF8',
      product: '#34D399',
      event: '#F472B6',
      location: '#FBBF24',
      textPrimary: '#E5EDF7',
      textSecondary: '#94A3B8',
      borderColor: '#26364B'
    }
  };

  /* ===========================================================================
   * 2. CENTRAL APPLICATION STATE
   * =========================================================================== */
  const LifeGraphState = {
    activeNav: 'nav-overview',
    activeDialect: 'gremlin', // 'gremlin' | 'sparql' | 'cypher'
    selectedNode: null,
    isPickMode: false,
    selectedHopDepth: 1,
    queryHistory: [
      {
        id: 1,
        dialect: 'gremlin',
        query: "g.V().hasLabel('Person').outE('COLLABORATES_WITH').inV().path()",
        timestamp: '10 mins ago',
        records: 4,
        duration: '12.4ms'
      },
      {
        id: 2,
        dialect: 'sparql',
        query: 'SELECT ?person ?org WHERE { ?person <urn:lifegraph:collaborates> ?org } LIMIT 10',
        timestamp: '25 mins ago',
        records: 12,
        duration: '18.1ms'
      }
    ],
    notifications: [
      { id: 1, title: 'Topology Partition Rebuilt', time: '5m ago', read: false, type: 'info' },
      { id: 2, title: 'Vector Embedding Drift (+14.3%)', time: '45m ago', read: false, type: 'warning' },
      { id: 3, title: 'Neptune Replica Synced (AZ-2)', time: '1h ago', read: false, type: 'success' }
    ],
    activeFilters: {
      Person: true,
      Organization: true,
      Product: true,
      Event: true,
      Location: true
    },
    stats: {
      totalNodes: 14892430,
      totalEdges: 89421105,
      vectorEmbeddings: 4250000,
      graphQueriesQps: 1842.6,
      systemStatus: 'Healthy (99.99%)',
      dataSources: 8
    }
  };

  /* ===========================================================================
   * 3. COMPREHENSIVE SAMPLE GRAPH & VECTOR DEMO DATASET
   * =========================================================================== */
  const LifeGraphData = {
    nodes: [
      {
        id: 'hub-root',
        label: 'Root Cluster Alpha',
        category: 'Hub',
        uri: 'urn:lifegraph:hub:root-01',
        description: 'Primary Topological Nexus & Central Routing Vertex',
        vectorWeight: 1.000,
        attributes: { tier: 'Primary', status: 'Online', throughput: '1.2 GB/s' }
      },
      {
        id: 'person-turing',
        label: 'Dr. Alan Turing',
        category: 'Person',
        uri: 'urn:lifegraph:person:7721',
        description: 'Chief Research Fellow in Neural & Mathematical Decryption',
        vectorWeight: 0.984,
        attributes: { role: 'Fellow', hIndex: 68, cluster: 'AI Theory' }
      },
      {
        id: 'person-vance',
        label: 'Mudasir Reyaz',
        category: 'Person',
        uri: 'urn:lifegraph:person:7722',
        description: 'Lead Graph Architect & Distributed Systems Scientist',
        vectorWeight: 0.965,
        attributes: { role: 'Architect', team: 'Core Systems', clearance: 'Level 5' }
      },
      {
        id: 'person-lin',
        label: 'Dr. Sophia Lin',
        category: 'Person',
        uri: 'usr:fellow:lin-482',
        description: 'Author of 14 publications in hierarchical graph-vector RAG',
        vectorWeight: 0.897,
        attributes: { role: 'Researcher', domain: 'HNSW Indexing' }
      },
      {
        id: 'org-graphlabs',
        label: 'DeepMind Graph Labs',
        category: 'Organization',
        uri: 'urn:lifegraph:org:0102',
        description: 'Enterprise AI Lab pioneering Graph Neural Networks & Reasoning',
        vectorWeight: 0.941,
        attributes: { founded: 2018, headquarters: 'London', nodesManaged: '45M' }
      },
      {
        id: 'org-mit',
        label: 'MIT CSAIL Network',
        category: 'Organization',
        uri: 'urn:lifegraph:org:mit:44',
        description: 'Academic collaborative research division on sparse graphs',
        vectorWeight: 0.880,
        attributes: { type: 'Academic', partnerships: 28 }
      },
      {
        id: 'org-zurich',
        label: 'Zurich Quantum Lab',
        category: 'Organization',
        uri: 'loc:org:zurich-091',
        description: 'Specialized entity focused on distributed graph vector computation',
        vectorWeight: 0.968,
        attributes: { qubits: 128, specialization: 'Annealing Algorithms' }
      },
      {
        id: 'product-core',
        label: 'NeptuneVector Core',
        category: 'Product',
        uri: 'urn:lifegraph:prod:9941',
        description: 'Enterprise distributed vector engine with native graph indices',
        vectorWeight: 0.912,
        attributes: { version: '2.4.0-rc2', license: 'Enterprise', memory: '128 GB' }
      },
      {
        id: 'product-hnsw',
        label: 'HNSW Neural Engine v3',
        category: 'Product',
        uri: 'prod:engine:vector-03',
        description: 'In-memory vector index optimizer supporting dynamic continuous subgraph partitioning',
        vectorWeight: 0.934,
        attributes: { indexType: 'HNSW', M: 16, efSearch: 100 }
      },
      {
        id: 'event-symposium',
        label: 'Quantum Leap 2026',
        category: 'Event',
        uri: 'urn:lifegraph:event:5512',
        description: 'Global symposium on Graph AI & high-dimensional embeddings',
        vectorWeight: 0.898,
        attributes: { date: '2026-11-18', attendees: 3400, format: 'Hybrid' }
      },
      {
        id: 'event-partition',
        label: 'Cluster Re-partitioning',
        category: 'Event',
        uri: 'urn:lifegraph:event:5513',
        description: 'Scheduled automated sharding operation across 4 sub-clusters',
        vectorWeight: 0.842,
        attributes: { execution: 'Automated', impact: 'Zero-Downtime' }
      },
      {
        id: 'loc-zurich',
        label: 'Zurich Data Cluster',
        category: 'Location',
        uri: 'loc:zurich:03',
        description: 'Tier-4 subterranean European data repository and compute node',
        vectorWeight: 0.905,
        attributes: { region: 'eu-central-1', latencyP99: '1.4ms', power: '100% Hydro' }
      },
      {
        id: 'loc-geneva',
        label: 'Geneva Fiber Hub',
        category: 'Location',
        uri: 'loc:geneva:01',
        description: 'High-bandwidth dark-fiber junction linking research centers',
        vectorWeight: 0.875,
        attributes: { bandwidth: '400 Gbps', status: 'Optimal' }
      }
    ],
    edges: [
      { id: 'e-hub-turing', source: 'hub-root', target: 'person-turing', label: 'COLLABORATES_WITH', weight: 0.95 },
      { id: 'e-hub-vance', source: 'hub-root', target: 'person-vance', label: 'MANAGED_BY', weight: 0.98 },
      { id: 'e-hub-org', source: 'hub-root', target: 'org-graphlabs', label: 'HOSTED_AT', weight: 0.92 },
      { id: 'e-hub-prod', source: 'hub-root', target: 'product-core', label: 'POWERS', weight: 0.99 },
      { id: 'e-hub-loc', source: 'hub-root', target: 'loc-zurich', label: 'LOCATED_IN', weight: 0.91 },

      { id: 'e-vance-graphlabs', source: 'person-vance', target: 'org-graphlabs', label: 'COLLABORATES_WITH', weight: 0.96 },
      { id: 'e-graphlabs-prod', source: 'org-graphlabs', target: 'product-core', label: 'INVESTED_IN', weight: 0.94 },
      { id: 'e-turing-prod', source: 'person-turing', target: 'product-core', label: 'PURCHASED', weight: 0.88 },
      { id: 'e-graphlabs-mit', source: 'org-graphlabs', target: 'org-mit', label: 'COLLABORATES_WITH', weight: 0.85 },
      { id: 'e-turing-symposium', source: 'person-turing', target: 'event-symposium', label: 'KEYNOTE_AT', weight: 0.93 },
      { id: 'e-symposium-loc', source: 'event-symposium', target: 'loc-zurich', label: 'LOCATED_IN', weight: 0.90 },
      { id: 'e-zurich-org', source: 'org-zurich', target: 'loc-zurich', label: 'LOCATED_IN', weight: 0.95 },
      { id: 'e-zurich-hnsw', source: 'org-zurich', target: 'product-hnsw', label: 'DEVELOPED', weight: 0.92 },
      { id: 'e-lin-hnsw', source: 'person-lin', target: 'product-hnsw', label: 'COLLABORATES_WITH', weight: 0.89 },
      { id: 'e-loc-geneva', source: 'loc-zurich', target: 'loc-geneva', label: 'CONNECTED_TO', weight: 0.97 },
      { id: 'e-event-partition', source: 'product-core', target: 'event-partition', label: 'TRIGGERED_BY', weight: 0.86 }
    ]
  };

  /* ===========================================================================
   * 4. SCRIPT & CDN DYNAMIC LOADER HELPER
   * =========================================================================== */
  function loadScriptAsync(src) {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) {
        return resolve();
      }
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      script.crossOrigin = 'anonymous';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load dependency: ${src}`));
      document.head.appendChild(script);
    });
  }

  /* ===========================================================================
   * 5. REUSABLE API CLIENT (FASTAPI / NEO4J READY)
   * =========================================================================== */
  const LifeGraphAPI = {
    /**
     * Executes queries against FastAPI backend with local simulator fallback
     */
    async queryGraph(queryText, dialect = 'gremlin', limit = 50) {
      const url = `${LifeGraphConfig.apiBaseUrl}${LifeGraphConfig.endpoints.graphQuery}`;
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryText, dialect, limit })
        });
        if (response.ok) {
          return await response.json();
        }
        throw new Error(`API returned HTTP ${response.status}`);
      } catch (err) {
        // Fallback: Local Simulated Query Processor
        console.info(`[LifeGraph AI] Backend unavailable at ${url}. Utilizing Client Simulated Engine. (${err.message})`);
        return this.simulateLocalQuery(queryText, dialect, limit);
      }
    },

    /**
     * Local client AST matching simulation
     */
    simulateLocalQuery(queryText, dialect, limit) {
      const lower = queryText.toLowerCase();
      let matchedNodes = LifeGraphData.nodes;

      if (lower.includes('person')) {
        matchedNodes = matchedNodes.filter(n => n.category === 'Person');
      } else if (lower.includes('org') || lower.includes('organization')) {
        matchedNodes = matchedNodes.filter(n => n.category === 'Organization');
      } else if (lower.includes('product')) {
        matchedNodes = matchedNodes.filter(n => n.category === 'Product');
      } else if (lower.includes('event')) {
        matchedNodes = matchedNodes.filter(n => n.category === 'Event');
      } else if (lower.includes('location')) {
        matchedNodes = matchedNodes.filter(n => n.category === 'Location');
      }

      // Slice by requested limit
      const records = matchedNodes.slice(0, limit).map((n, idx) => {
        const connectedEdges = LifeGraphData.edges.filter(e => e.source === n.id || e.target === n.id);
        const neighborIds = connectedEdges.map(e => e.source === n.id ? e.target : e.source).slice(0, 2).join(', ');
        return {
          index: idx + 1,
          entityId: n.uri,
          label: n.category,
          properties: `name: "${n.label}", weight: ${n.vectorWeight}`,
          connectedNodes: neighborIds || 'cluster:alpha:01',
          vectorWeight: n.vectorWeight
        };
      });

      return {
        status: 'simulated_success',
        dialect,
        executionTimeMs: (Math.random() * 6 + 7).toFixed(1),
        rowCount: records.length,
        records
      };
    },

    /**
     * Vector Similarity search with local embedding simulation
     */
    async searchVectors(queryPrompt, topK = 10, threshold = 0.85, metric = 'cosine') {
      const url = `${LifeGraphConfig.apiBaseUrl}${LifeGraphConfig.endpoints.vectorSearch}`;
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: queryPrompt, top_k: topK, threshold, metric })
        });
        if (response.ok) {
          return await response.json();
        }
        throw new Error(`API returned HTTP ${response.status}`);
      } catch (err) {
        return this.simulateVectorSearch(queryPrompt, topK, threshold, metric);
      }
    },

    simulateVectorSearch(queryPrompt, topK, threshold, metric) {
      const qTokens = queryPrompt.toLowerCase().split(/\W+/).filter(Boolean);

      const scored = LifeGraphData.nodes.map(node => {
        const textBlob = `${node.label} ${node.description} ${node.category}`.toLowerCase();
        let matches = 0;
        qTokens.forEach(t => {
          if (textBlob.includes(t)) matches += 1;
        });

        // Compute simulated similarity score
        const tokenOverlap = qTokens.length > 0 ? (matches / qTokens.length) * 0.35 : 0;
        const baseline = node.vectorWeight * 0.65;
        const rawScore = baseline + tokenOverlap;
        const similarity = Math.min(0.992, Math.max(0.51, rawScore));
        const distance = (1 - similarity).toFixed(3);

        return {
          id: node.id,
          title: node.label,
          uri: node.uri,
          category: node.category,
          snippet: node.description,
          similarityScore: similarity,
          distance
        };
      });

      // Filter by threshold and sort descending
      const filtered = scored
        .filter(item => item.similarityScore >= threshold)
        .sort((a, b) => b.similarityScore - a.similarityScore)
        .slice(0, topK);

      return {
        query: queryPrompt,
        threshold,
        metric,
        executionTimeSec: (Math.random() * 0.015 + 0.008).toFixed(3),
        totalMatches: filtered.length,
        results: filtered
      };
    }
  };

  /* ===========================================================================
   * 6. GRAPH VISUALIZER MODULE (CYTOSCAPE.JS INTEGRATION + CANVAS FALLBACK)
   * =========================================================================== */
  const GraphVisualizer = {
    cy: null,
    container: null,
    isInitialized: false,
    currentLayout: 'cose',

    async init() {
      this.container = document.getElementById('graph-canvas-container');
      if (!this.container) return;

      // Attempt to load Cytoscape from CDN
      try {
        if (typeof window.cytoscape === 'undefined') {
          await loadScriptAsync(LifeGraphConfig.cytoscapeCdn);
        }
      } catch (err) {
        console.warn('[LifeGraph AI] Cytoscape.js CDN unavailable. Running Canvas Graphic Fallback.', err);
      }

      if (typeof window.cytoscape !== 'undefined') {
        this.initCytoscape();
      } else {
        this.initCanvasFallback();
      }

      this.bindToolbarEvents();
      this.bindCategoryFilters();
      this.isInitialized = true;
    },

    initCytoscape() {
      // Hide static mock markup gracefully
      const mockElem = document.getElementById('central-nodes-mock');
      if (mockElem) {
        mockElem.style.display = 'none';
      }

      // Convert our data into Cytoscape elements
      const elements = [
        ...LifeGraphData.nodes.map(n => ({
          data: {
            id: n.id,
            label: n.label,
            category: n.category,
            uri: n.uri,
            weight: n.vectorWeight
          }
        })),
        ...LifeGraphData.edges.map(e => ({
          data: {
            id: e.id,
            source: e.source,
            target: e.target,
            label: e.label,
            weight: e.weight
          }
        }))
      ];

      // Node colors map
      const colorMap = {
        Hub: LifeGraphConfig.colors.cyan,
        Person: LifeGraphConfig.colors.person,
        Organization: LifeGraphConfig.colors.org,
        Product: LifeGraphConfig.colors.product,
        Event: LifeGraphConfig.colors.event,
        Location: LifeGraphConfig.colors.location
      };

      try {
        this.cy = window.cytoscape({
          container: this.container,
          elements,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'color': LifeGraphConfig.colors.textPrimary,
                'font-family': 'JetBrains Mono, monospace',
                'font-size': '11px',
                'text-valign': 'bottom',
                'text-margin-y': 6,
                'background-color': '#111C2D',
                'border-width': 2,
                'border-color': ele => colorMap[ele.data('category')] || LifeGraphConfig.colors.cyan,
                'width': ele => ele.data('category') === 'Hub' ? 56 : 38,
                'height': ele => ele.data('category') === 'Hub' ? 56 : 38,
                'text-background-color': 'rgba(12, 20, 34, 0.85)',
                'text-background-opacity': 0.9,
                'text-background-padding': '3px',
                'text-background-shape': 'roundrectangle',
                'transition-property': 'background-color, border-color, width, height, opacity',
                'transition-duration': '0.2s'
              }
            },
            {
              selector: 'node:selected',
              style: {
                'border-width': 3,
                'border-color': '#FFFFFF',
                'shadow-blur': 18,
                'shadow-color': LifeGraphConfig.colors.cyan,
                'shadow-opacity': 0.85
              }
            },
            {
              selector: 'node.highlighted',
              style: {
                'border-width': 3,
                'shadow-blur': 12,
                'shadow-color': LifeGraphConfig.colors.cyan,
                'opacity': 1.0
              }
            },
            {
              selector: 'node.faded',
              style: {
                'opacity': 0.2
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 1.8,
                'line-color': '#26364B',
                'target-arrow-color': '#26364B',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '8px',
                'color': LifeGraphConfig.colors.textSecondary,
                'font-family': 'monospace',
                'text-rotation': 'autorotate',
                'text-background-color': '#0C1422',
                'text-background-opacity': 0.8,
                'text-background-padding': '2px',
                'transition-property': 'line-color, target-arrow-color, width, opacity',
                'transition-duration': '0.2s'
              }
            },
            {
              selector: 'edge.highlighted',
              style: {
                'line-color': LifeGraphConfig.colors.cyan,
                'target-arrow-color': LifeGraphConfig.colors.cyan,
                'width': 2.8,
                'opacity': 1.0
              }
            },
            {
              selector: 'edge.faded',
              style: {
                'opacity': 0.15
              }
            }
          ],
          layout: {
            name: 'cose',
            idealEdgeLength: 100,
            nodeOverlap: 20,
            refresh: 20,
            fit: true,
            padding: 40,
            randomize: false,
            componentSpacing: 100,
            nodeRepulsion: 400000,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80,
            numIter: 1000,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0
          }
        });

        // Tap Node Interaction
        this.cy.on('tap', 'node', evt => {
          const node = evt.target;
          this.handleNodeSelect(node);
        });

        // Tap Background to Reset Highlights
        this.cy.on('tap', evt => {
          if (evt.target === this.cy) {
            this.clearHighlights();
          }
        });

        this.updateHudMetrics(elements.length, LifeGraphData.edges.length);
      } catch (e) {
        console.error('[LifeGraph AI] Failed to initialize Cytoscape instance:', e);
        this.initCanvasFallback();
      }
    },

    initCanvasFallback() {
      // Keep static mock clean and active with CSS hover & selection
      const mockNodes = document.querySelectorAll('.mock-node');
      mockNodes.forEach(node => {
        node.style.cursor = 'pointer';
        node.addEventListener('click', e => {
          e.stopPropagation();
          mockNodes.forEach(n => n.classList.remove('selected'));
          node.classList.add('selected');

          const title = node.getAttribute('title') || node.id;
          UIController.showToast(`Selected Node: ${title}`, 'info');

          // If K-Hop pick mode is active, bind it
          if (LifeGraphState.isPickMode) {
            const targetInput = document.getElementById('khop-target-node');
            if (targetInput) targetInput.value = `urn:lifegraph:${node.id}:demo`;
            LifeGraphState.isPickMode = false;
            UIController.showToast(`Node ${node.id} bound to K-Hop Root`, 'success');
          }
        });
      });
    },

    handleNodeSelect(node) {
      const nodeData = node.data();
      LifeGraphState.selectedNode = nodeData;

      // Highlight 1-hop connected neighborhood
      this.cy.elements().removeClass('highlighted faded');
      const neighborhood = node.neighborhood().add(node);
      neighborhood.addClass('highlighted');
      this.cy.elements().not(neighborhood).addClass('faded');

      // Update HUD metrics
      const hudRendered = document.getElementById('hud-rendered-nodes');
      if (hudRendered) {
        hudRendered.innerHTML = `Selected: <strong>${nodeData.label}</strong> (${nodeData.category})`;
      }

      // If Pick mode is active, insert into K-Hop input
      if (LifeGraphState.isPickMode) {
        const input = document.getElementById('khop-target-node');
        if (input) {
          input.value = nodeData.uri || nodeData.id;
          UIController.showToast(`Root Node Selected: ${nodeData.label}`, 'success');
        }
        LifeGraphState.isPickMode = false;
      } else {
        UIController.showToast(`Node Inspected: ${nodeData.label} [${nodeData.category}] (Vector Weight: ${nodeData.weight})`, 'info');
      }
    },

    clearHighlights() {
      if (this.cy) {
        this.cy.elements().removeClass('highlighted faded');
      }
      const hudRendered = document.getElementById('hud-rendered-nodes');
      if (hudRendered) {
        hudRendered.textContent = `${LifeGraphData.nodes.length} Nodes`;
      }
    },

    bindToolbarEvents() {
      // Zoom In
      document.getElementById('btn-graph-zoom-in')?.addEventListener('click', () => {
        if (this.cy) this.cy.zoom(this.cy.zoom() * 1.25);
      });

      // Zoom Out
      document.getElementById('btn-graph-zoom-out')?.addEventListener('click', () => {
        if (this.cy) this.cy.zoom(this.cy.zoom() * 0.8);
      });

      // Fit to Screen
      document.getElementById('btn-graph-fit')?.addEventListener('click', () => {
        if (this.cy) this.cy.fit(null, 40);
      });

      // Pause/Resume Simulation
      let isPaused = false;
      document.getElementById('btn-graph-pause')?.addEventListener('click', e => {
        isPaused = !isPaused;
        const icon = e.currentTarget.querySelector('i');
        if (icon) {
          icon.className = isPaused ? 'fa-solid fa-play' : 'fa-solid fa-pause';
        }
        UIController.showToast(isPaused ? 'Physics Simulation Paused' : 'Physics Simulation Resumed', 'info');
      });

      // Export Snapshot
      document.getElementById('btn-graph-export')?.addEventListener('click', () => {
        this.exportGraphSnapshot();
      });

      // View Modes: 2D, 3D, Vector
      const viewButtons = [
        { id: 'btn-view-2d', layout: 'cose', modeName: '2D Force Layout' },
        { id: 'btn-view-3d', layout: 'circle', modeName: '3D Universe Projection' },
        { id: 'btn-view-vector', layout: 'concentric', modeName: 'Vector Embedding Space' }
      ];

      viewButtons.forEach(btnConfig => {
        const btn = document.getElementById(btnConfig.id);
        if (!btn) return;
        btn.addEventListener('click', () => {
          document.querySelectorAll('#graph-toolbar .btn-control').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          const tag = document.getElementById('projection-mode-tag');
          if (tag) tag.textContent = btnConfig.modeName;

          if (this.cy) {
            this.cy.layout({ name: btnConfig.layout, animate: true, animationDuration: 600 }).run();
          }
          UIController.showToast(`Switched to ${btnConfig.modeName}`, 'info');
        });
      });
    },

    bindCategoryFilters() {
      const categoryInputs = [
        { id: 'filter-person', category: 'Person' },
        { id: 'filter-organization', category: 'Organization' },
        { id: 'filter-product', category: 'Product' },
        { id: 'filter-event', category: 'Event' },
        { id: 'filter-location', category: 'Location' }
      ];

      categoryInputs.forEach(({ id, category }) => {
        const checkbox = document.getElementById(id);
        if (!checkbox) return;

        checkbox.addEventListener('change', () => {
          const isVisible = checkbox.checked;
          LifeGraphState.activeFilters[category] = isVisible;

          if (this.cy) {
            const nodes = this.cy.nodes(`[category = "${category}"]`);
            if (isVisible) {
              nodes.show();
            } else {
              nodes.hide();
            }
          }
          UIController.showToast(`Filter: ${category} ${isVisible ? 'Shown' : 'Hidden'}`, 'info');
        });
      });
    },

    exportGraphSnapshot() {
      if (this.cy) {
        try {
          const pngBase64 = this.cy.png({ full: true, bg: LifeGraphConfig.colors.bgMain, scale: 2 });
          const a = document.createElement('a');
          a.href = pngBase64;
          a.download = `lifegraph-snapshot-${Date.now()}.png`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          UIController.showToast('High-Res Graph Snapshot Exported (.png)', 'success');
          return;
        } catch (err) {
          console.warn('[LifeGraph AI] PNG export failed:', err);
        }
      }
      UIController.showToast('Graph schema topology exported as JSON bundle', 'success');
    },

    updateHudMetrics(nodesCount, edgesCount) {
      const nodesElem = document.getElementById('hud-rendered-nodes');
      const edgesElem = document.getElementById('hud-rendered-edges');
      if (nodesElem) nodesElem.textContent = `${nodesCount} Nodes`;
      if (edgesElem) edgesElem.textContent = `${edgesCount} Edges`;
    }
  };

  /* ===========================================================================
   * 7. QUERY CONSOLE CONTROLLER
   * =========================================================================== */
  const QueryConsoleManager = {
    sampleQueries: {
      gremlin: `// Traverse Person to Collaborating Organizations\ng.V().hasLabel('Person').has('name', 'Elena Vance')\n  .outE('COLLABORATES_WITH')\n  .inV().hasLabel('Organization')\n  .path().by('name')`,
      sparql: `PREFIX lg: <urn:lifegraph:>\nSELECT ?person ?org ?weight WHERE {\n  ?person lg:collaborates_with ?org .\n  ?person lg:vectorWeight ?weight .\n  FILTER (?weight > 0.90)\n} LIMIT 25`,
      cypher: `MATCH (p:Person)-[r:COLLABORATES_WITH]->(o:Organization)\nWHERE p.vectorWeight >= 0.85\nRETURN p.name AS Specialist, type(r) AS Relation, o.name AS Entity\nORDER BY p.vectorWeight DESC LIMIT 10`
    },

    init() {
      this.bindDialectTabs();
      this.bindExecuteQuery();
      this.bindClearAndFormat();
      this.bindHistoryModal();
    },

    bindDialectTabs() {
      const tabs = [
        { id: 'tab-gremlin', dialect: 'gremlin', label: 'Active: Apache TinkerPop Gremlin 3.7' },
        { id: 'tab-sparql', dialect: 'sparql', label: 'Active: W3C SPARQL 1.1 Query Engine' },
        { id: 'tab-cypher', dialect: 'cypher', label: 'Active: openCypher 9 (Neo4j Compatible)' }
      ];

      tabs.forEach(({ id, dialect, label }) => {
        const btn = document.getElementById(id);
        if (!btn) return;

        btn.addEventListener('click', () => {
          document.querySelectorAll('.query-tabs .tab-btn').forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
          });
          btn.classList.add('active');
          btn.setAttribute('aria-selected', 'true');

          LifeGraphState.activeDialect = dialect;
          const dialectLabel = document.getElementById('active-dialect-label');
          if (dialectLabel) dialectLabel.textContent = label;

          // Populate with appropriate sample query if editor is at default
          const textarea = document.getElementById('query-input-area');
          if (textarea) {
            textarea.value = this.sampleQueries[dialect];
          }
        });
      });
    },

    bindExecuteQuery() {
      const executeBtn = document.getElementById('btn-execute-query');
      const textarea = document.getElementById('query-input-area');

      if (!executeBtn || !textarea) return;

      executeBtn.addEventListener('click', async () => {
        const query = textarea.value.trim();
        if (!query) {
          UIController.showToast('Please enter a graph query to execute.', 'warning');
          textarea.focus();
          return;
        }

        // Visual loading state
        const originalContent = executeBtn.innerHTML;
        executeBtn.disabled = true;
        executeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> <span>Executing AST...</span>';

        try {
          const limitSelect = document.getElementById('query-limit-select');
          const limit = limitSelect ? parseInt(limitSelect.value, 10) : 50;

          const response = await LifeGraphAPI.queryGraph(query, LifeGraphState.activeDialect, limit);
          this.renderResults(response);

          // Add to query history
          LifeGraphState.queryHistory.unshift({
            id: Date.now(),
            dialect: LifeGraphState.activeDialect,
            query: query.substring(0, 80) + (query.length > 80 ? '...' : ''),
            timestamp: 'Just now',
            records: response.rowCount,
            duration: `${response.executionTimeMs}ms`
          });

          // Log in Recent Activity
          AnalyticsManager.addActivityEvent(
            'cyan',
            `Executed ${LifeGraphState.activeDialect.toUpperCase()} traversal (${response.rowCount} records in ${response.executionTimeMs}ms).`
          );

          UIController.showToast(`Query Succeeded: ${response.rowCount} records returned in ${response.executionTimeMs}ms. (AST Simulation)`, 'success');
        } catch (err) {
          console.error(err);
          UIController.showToast(`Query Error: ${err.message}`, 'danger');
        } finally {
          executeBtn.disabled = false;
          executeBtn.innerHTML = originalContent;
        }
      });
    },

    renderResults(response) {
      const tbody = document.getElementById('results-table-body');
      const timeElem = document.getElementById('result-time');
      const countElem = document.getElementById('result-count');

      if (timeElem) timeElem.innerHTML = `Execution Time: <strong>${response.executionTimeMs}ms</strong>`;
      if (countElem) countElem.innerHTML = `Rows: <strong>${response.rowCount} Records</strong>`;

      if (!tbody) return;

      if (!response.records || response.records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color: var(--text-muted);"><i class="fa-solid fa-triangle-exclamation"></i> No entities matching traversal conditions.</td></tr>`;
        return;
      }

      tbody.innerHTML = response.records.map(r => `
        <tr>
          <td>${r.index}</td>
          <td><code>${r.entityId}</code></td>
          <td><span class="badge badge-${r.label.toLowerCase()}">${r.label}</span></td>
          <td><code>${r.properties}</code></td>
          <td><code>${r.connectedNodes}</code></td>
          <td>${r.vectorWeight}</td>
        </tr>
      `).join('');
    },

    bindClearAndFormat() {
      const clearBtn = document.getElementById('btn-clear-query');
      const formatBtn = document.getElementById('btn-query-format');
      const textarea = document.getElementById('query-input-area');

      if (clearBtn && textarea) {
        clearBtn.addEventListener('click', () => {
          textarea.value = '';
          const tbody = document.getElementById('results-table-body');
          if (tbody) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color: var(--text-muted);">Console cleared. Enter a traversal query and click Execute.</td></tr>`;
          }
          UIController.showToast('Query Console cleared', 'info');
        });
      }

      if (formatBtn && textarea) {
        formatBtn.addEventListener('click', () => {
          let text = textarea.value;
          // Simple multi-line formatter for fluent graph traversals
          text = text
            .replace(/\s*\.\s*/g, '\n  .')
            .replace(/\{\s*/g, '{\n  ')
            .replace(/\s*\}\s*/g, '\n}');
          textarea.value = text;
          UIController.showToast('Query formatted and aligned', 'info');
        });
      }
    },

    bindHistoryModal() {
      const historyBtn = document.getElementById('btn-query-history');
      if (!historyBtn) return;

      historyBtn.addEventListener('click', () => {
        const historyList = LifeGraphState.queryHistory
          .slice(0, 5)
          .map((h, i) => `#${i + 1} [${h.dialect.toUpperCase()}] ${h.query} (${h.duration})`)
          .join('\n');

        alert(`Recent LifeGraph AI Query History:\n\n${historyList}\n\nTip: You can select any dialect tab to load built-in templates.`);
      });
    }
  };

  /* ===========================================================================
   * 8. K-HOP NEIGHBORHOOD EXPLORER MODULE
   * =========================================================================== */
  const KHopExplorerManager = {
    init() {
      this.bindHopRadioButtons();
      this.bindPickMode();
      this.bindTraverseAction();
    },

    bindHopRadioButtons() {
      const radios = document.querySelectorAll('input[name="khop-depth"]');
      radios.forEach(radio => {
        radio.addEventListener('change', () => {
          document.querySelectorAll('.hop-radio-label').forEach(lbl => lbl.classList.remove('active'));
          radio.closest('.hop-radio-label')?.classList.add('active');
          LifeGraphState.selectedHopDepth = parseInt(radio.value, 10);
          UIController.showToast(`K-Hop Radius set to ${radio.value}-Hop`, 'info');
        });
      });
    },

    bindPickMode() {
      const pickBtn = document.getElementById('btn-khop-pick-canvas');
      if (!pickBtn) return;

      pickBtn.addEventListener('click', () => {
        LifeGraphState.isPickMode = true;
        UIController.showToast('Crosshair Active: Click any node on the Graph Canvas to set Root', 'info');
      });
    },

    bindTraverseAction() {
      const traverseBtn = document.getElementById('btn-traverse-khop');
      const targetInput = document.getElementById('khop-target-node');
      const placeholderCard = document.getElementById('khop-placeholder-card');

      if (!traverseBtn || !targetInput) return;

      traverseBtn.addEventListener('click', () => {
        const rootUri = targetInput.value.trim();
        if (!rootUri) {
          UIController.showToast('Please specify a root vertex identifier.', 'warning');
          targetInput.focus();
          return;
        }

        const depth = LifeGraphState.selectedHopDepth || 1;
        const direction = document.getElementById('khop-direction')?.value || 'both';

        // Perform breadth-first traversal simulation
        const discovered = this.performBfsTraversal(rootUri, depth);

        if (placeholderCard) {
          placeholderCard.innerHTML = `
            <i class="fa-solid fa-circle-check placeholder-icon" style="color: var(--color-success)"></i>
            <p class="placeholder-title">${depth}-Hop Neighborhood Discovered</p>
            <p class="placeholder-desc">
              Root <code>${rootUri}</code> expanded across <strong>${discovered.vertices.length} vertices</strong> and
              <strong>${discovered.edges.length} connecting edges</strong> (${discovered.latencyMs}ms).
            </p>
            <div style="display:flex; flex-wrap:wrap; gap:6px; justify-content:center; margin-top:8px;">
              ${discovered.vertices.map(v => `<span class="badge badge-${v.category.toLowerCase()}">${v.label}</span>`).join('')}
            </div>
          `;
        }

        // Highlight in Cytoscape if available
        if (GraphVisualizer.cy) {
          const cy = GraphVisualizer.cy;
          cy.elements().removeClass('highlighted faded');
          const matchedRoot = cy.nodes().filter(n => n.data('uri') === rootUri || n.data('id') === rootUri);

          if (matchedRoot.length > 0) {
            let collection = matchedRoot;
            for (let i = 0; i < depth; i++) {
              collection = collection.add(collection.neighborhood());
            }
            collection.addClass('highlighted');
            cy.elements().not(collection).addClass('faded');
            cy.animate({ fit: { eles: collection, padding: 50 }, duration: 400 });
          }
        }

        AnalyticsManager.addActivityEvent('green', `K-Hop expansion (${depth}-Hop) executed on ${rootUri}.`);
        UIController.showToast(`K-Hop Explorer: ${discovered.vertices.length} nodes isolated in ${depth}-Hop scope.`, 'success');
      });
    },

    performBfsTraversal(rootUri, depth) {
      // Find starting node
      const rootNode = LifeGraphData.nodes.find(n => n.uri === rootUri || n.id === rootUri) || LifeGraphData.nodes[1];

      const visitedNodes = new Set([rootNode.id]);
      const visitedEdges = new Set();
      let currentFrontier = [rootNode.id];

      for (let hop = 0; hop < depth; hop++) {
        const nextFrontier = [];
        currentFrontier.forEach(currId => {
          LifeGraphData.edges.forEach(edge => {
            let neighbor = null;
            if (edge.source === currId && !visitedNodes.has(edge.target)) {
              neighbor = edge.target;
            } else if (edge.target === currId && !visitedNodes.has(edge.source)) {
              neighbor = edge.source;
            }

            if (neighbor) {
              visitedNodes.add(neighbor);
              visitedEdges.add(edge.id);
              nextFrontier.push(neighbor);
            }
          });
        });
        currentFrontier = nextFrontier;
      }

      const vertices = LifeGraphData.nodes.filter(n => visitedNodes.has(n.id));
      const edges = LifeGraphData.edges.filter(e => visitedEdges.has(e.id));

      return {
        root: rootNode,
        vertices,
        edges,
        latencyMs: (Math.random() * 4 + 3.2).toFixed(1)
      };
    }
  };

  /* ===========================================================================
   * 9. VECTOR SEMANTIC SEARCH CONTROLLER
   * =========================================================================== */
  const VectorSearchManager = {
    init() {
      this.bindThresholdSlider();
      this.bindSearchExecution();
    },

    bindThresholdSlider() {
      const slider = document.getElementById('similarity-threshold');
      const display = document.getElementById('threshold-val-display');

      if (!slider || !display) return;

      slider.addEventListener('input', () => {
        const val = parseFloat(slider.value).toFixed(2);
        display.innerHTML = `&ge; ${val}`;
      });
    },

    bindSearchExecution() {
      const searchBtn = document.getElementById('btn-vector-search');
      const searchInput = document.getElementById('vector-search-input');

      if (!searchBtn || !searchInput) return;

      const triggerSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) {
          UIController.showToast('Please enter a semantic prompt or vector concept.', 'warning');
          searchInput.focus();
          return;
        }

        const topK = parseInt(document.getElementById('top-k-select')?.value || '10', 10);
        const threshold = parseFloat(document.getElementById('similarity-threshold')?.value || '0.85');
        const metric = document.getElementById('search-mode-select')?.value || 'cosine';

        searchBtn.disabled = true;
        const origHtml = searchBtn.innerHTML;
        searchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Searching HNSW Index...</span>';

        try {
          const response = await LifeGraphAPI.searchVectors(query, topK, threshold, metric);
          this.renderResults(response);
          UIController.showToast(`Vector Search: Found ${response.totalMatches} embeddings (Score &ge; ${threshold})`, 'success');
        } catch (err) {
          console.error(err);
          UIController.showToast('Vector search simulation error', 'danger');
        } finally {
          searchBtn.disabled = false;
          searchBtn.innerHTML = origHtml;
        }
      };

      searchBtn.addEventListener('click', triggerSearch);
      searchInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
          e.preventDefault();
          triggerSearch();
        }
      });
    },

    renderResults(response) {
      const listContainer = document.getElementById('vector-results-list');
      const countTag = document.getElementById('vector-results-count');

      if (countTag) {
        countTag.textContent = `Top ${response.totalMatches} Results Returned (${response.executionTimeSec}s - Simulated HNSW)`;
      }

      if (!listContainer) return;

      if (!response.results || response.results.length === 0) {
        listContainer.innerHTML = `
          <div style="text-align:center; padding: 28px 16px; color: var(--text-muted); background: var(--bg-card-inner); border-radius: var(--radius-md); border: 1px dashed var(--border-color);">
            <i class="fa-solid fa-brain" style="font-size: 1.8rem; margin-bottom: 8px; color: var(--text-muted);"></i>
            <p style="font-weight: 600; color: var(--text-primary);">No Embeddings Met Threshold (${response.threshold})</p>
            <p style="font-size: 0.75rem;">Try lowering the similarity threshold or refining your search concepts.</p>
          </div>
        `;
        return;
      }

      listContainer.innerHTML = response.results.map((item, idx) => {
        const percent = (item.similarityScore * 100).toFixed(1);
        return `
          <article class="vector-result-card" id="vector-res-dyn-${idx}">
            <div class="result-card-header">
              <span class="badge badge-${item.category.toLowerCase()}">${item.category}</span>
              <span class="similarity-score">
                <i class="fa-solid fa-chart-simple" aria-hidden="true"></i> ${percent}% Match
              </span>
            </div>
            <h4 class="result-entity-title">${item.title}</h4>
            <p class="result-snippet">${item.snippet}</p>
            <div class="result-card-meta">
              <span>Node: <code>${item.uri}</code></span>
              <span>Distance: ${item.distance}</span>
            </div>
          </article>
        `;
      }).join('');
    }
  };

  /* ===========================================================================
   * 10. AI INTELLIGENCE ACTIONS CONTROLLER
   * =========================================================================== */
  const AIIntelligenceManager = {
    init() {
      // Pattern Discovery: Isolate Motifs
      document.getElementById('btn-export-patterns')?.addEventListener('click', () => {
        UIController.showToast('Pattern Discovery: Extracted 47 triadic subgraph motifs to JSON schema.', 'success');
        AnalyticsManager.addActivityEvent('cyan', 'Exported 47 recurrent graph motifs for deep learning analysis.');
      });

      // Anomaly Detection: Quarantine Node
      document.getElementById('btn-quarantine-node')?.addEventListener('click', () => {
        const confirmed = confirm('Quarantine target node usr:trans:99120 from active cluster routing?');
        if (confirmed) {
          UIController.showToast('Node usr:trans:99120 isolated into sandbox quarantine.', 'warning');
          AnalyticsManager.addActivityEvent('amber', 'Quarantined outlier entity usr:trans:99120 due to topology drift.');
        }
      });

      // Predictive Risk: Run Monte Carlo Simulation
      document.getElementById('btn-run-simulation')?.addEventListener('click', () => {
        const fill = document.getElementById('risk-progress-fill');
        const valElem = document.getElementById('risk-score-val');

        if (fill && valElem) {
          fill.style.width = '35%';
          valElem.textContent = 'Simulating (1,000 runs)...';
          valElem.style.color = LifeGraphConfig.colors.warning;

          setTimeout(() => {
            const randomRisk = (Math.random() * 6 + 10).toFixed(1);
            fill.style.width = `${randomRisk}%`;
            valElem.textContent = `Low (${randomRisk}%)`;
            valElem.style.color = LifeGraphConfig.colors.success;
            UIController.showToast(`Monte Carlo Completed: Systemic Risk evaluated at ${randomRisk}%.`, 'success');
            AnalyticsManager.addActivityEvent('blue', `Simulated link cascade failures across 10,000 edge permutations.`);
          }, 800);
        }
      });

      // AI-Generated Insights: Apply Optimization
      document.getElementById('btn-apply-insight')?.addEventListener('click', () => {
        UIController.showToast('Federated sub-region optimization dispatched to Neptune cluster manager.', 'success');
        AnalyticsManager.addActivityEvent('purple', 'Applied automated graph federation policy between Zurich & Geneva.');
      });
    }
  };

  /* ===========================================================================
   * 11. ANALYTICS & TELEMETRY CONTROLLER (CHART.JS INTEGRATION + FALLBACK)
   * =========================================================================== */
  const AnalyticsManager = {
    charts: {},

    async init() {
      try {
        if (typeof window.Chart === 'undefined') {
          await loadScriptAsync(LifeGraphConfig.chartJsCdn);
        }
      } catch (err) {
        console.warn('[LifeGraph AI] Chart.js CDN not reachable. Telemetry will run in lightweight SVG mode.', err);
      }

      if (typeof window.Chart !== 'undefined') {
        this.renderChartsWithChartJs();
      } else {
        this.renderSvgFallbackCharts();
      }

      this.startLiveTelemetryTicker();
    },

    renderChartsWithChartJs() {
      const Chart = window.Chart;

      // 1. Latency Time-Series Chart
      const latencyContainer = document.getElementById('chart-query-latency');
      if (latencyContainer) {
        latencyContainer.innerHTML = '<canvas id="canvas-latency" height="120"></canvas>';
        const ctx = document.getElementById('canvas-latency').getContext('2d');
        this.charts.latency = new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['18:00', '18:15', '18:30', '18:45', '19:00', '19:15', '19:30'],
            datasets: [
              {
                label: 'P99 Latency (ms)',
                data: [19.2, 17.8, 18.9, 16.4, 19.5, 17.9, 18.2],
                borderColor: LifeGraphConfig.colors.cyan,
                backgroundColor: 'rgba(34, 211, 238, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.35,
                pointRadius: 2
              },
              {
                label: 'P50 Latency (ms)',
                data: [3.8, 3.2, 3.5, 3.1, 4.0, 3.3, 3.4],
                borderColor: LifeGraphConfig.colors.success,
                borderWidth: 1.5,
                tension: 0.35,
                pointRadius: 1
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              x: { grid: { color: 'rgba(38, 54, 75, 0.4)' }, ticks: { color: LifeGraphConfig.colors.textSecondary, font: { size: 9 } } },
              y: { grid: { color: 'rgba(38, 54, 75, 0.4)' }, ticks: { color: LifeGraphConfig.colors.textSecondary, font: { size: 9 } } }
            }
          }
        });
      }

      // 2. Query Throughput Chart
      const throughputContainer = document.getElementById('chart-query-throughput');
      if (throughputContainer) {
        throughputContainer.innerHTML = '<canvas id="canvas-throughput" height="120"></canvas>';
        const ctx = document.getElementById('canvas-throughput').getContext('2d');
        this.charts.throughput = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['10m', '8m', '6m', '4m', '2m', 'Now'],
            datasets: [
              {
                label: 'Read Ops',
                data: [1420, 1510, 1490, 1580, 1620, 1517],
                backgroundColor: 'rgba(59, 130, 246, 0.7)'
              },
              {
                label: 'Write Ops',
                data: [310, 290, 340, 320, 310, 325],
                backgroundColor: 'rgba(34, 211, 238, 0.7)'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { stacked: true, grid: { display: false }, ticks: { color: LifeGraphConfig.colors.textSecondary, font: { size: 9 } } },
              y: { stacked: true, grid: { color: 'rgba(38, 54, 75, 0.4)' }, ticks: { color: LifeGraphConfig.colors.textSecondary, font: { size: 9 } } }
            }
          }
        });
      }

      // 3. Storage Allocation Doughnut Chart
      const storageContainer = document.getElementById('chart-storage-growth');
      if (storageContainer) {
        storageContainer.innerHTML = '<canvas id="canvas-storage" height="120"></canvas>';
        const ctx = document.getElementById('canvas-storage').getContext('2d');
        this.charts.storage = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Graph DB (1.42 TB)', 'Vector Index (680 GB)', 'WAL Cache (42 GB)'],
            datasets: [{
              data: [1420, 680, 42],
              backgroundColor: [LifeGraphConfig.colors.blue, LifeGraphConfig.colors.purple, LifeGraphConfig.colors.cyan],
              borderWidth: 2,
              borderColor: LifeGraphConfig.colors.bgPanel
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: { color: LifeGraphConfig.colors.textSecondary, font: { size: 9 } }
              }
            }
          }
        });
      }
    },

    renderSvgFallbackCharts() {
      // Graceful high-tech SVG sparklines when Chart.js CDN is unavailable
      const latencyContainer = document.getElementById('chart-query-latency');
      if (latencyContainer) {
        latencyContainer.innerHTML = `
          <svg viewBox="0 0 300 80" style="width:100%; height:80px; overflow:visible;">
            <defs>
              <linearGradient id="grad-latency" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="#22D3EE" stop-opacity="0.0"/>
              </linearGradient>
            </defs>
            <path d="M 0 50 Q 50 30, 100 45 T 200 35 T 300 40 L 300 80 L 0 80 Z" fill="url(#grad-latency)" />
            <path d="M 0 50 Q 50 30, 100 45 T 200 35 T 300 40" fill="none" stroke="#22D3EE" stroke-width="2" />
          </svg>
        `;
      }
    },

    startLiveTelemetryTicker() {
      // Subtle realistic metric fluctuation every 4 seconds
      setInterval(() => {
        const qpsElem = document.getElementById('val-graph-queries');
        if (qpsElem) {
          const delta = (Math.random() * 8 - 4);
          const current = 1842.6 + delta;
          qpsElem.textContent = `${current.toFixed(1)} req/s`;
        }

        const hudFps = document.getElementById('hud-fps');
        if (hudFps) {
          const fps = (59.4 + Math.random() * 0.8).toFixed(1);
          hudFps.textContent = `${fps} FPS`;
        }
      }, 4000);
    },

    addActivityEvent(bulletColor, message) {
      const list = document.getElementById('activity-list');
      if (!list) return;

      const item = document.createElement('li');
      item.className = 'activity-item';
      item.innerHTML = `
        <span class="activity-bullet ${bulletColor}" aria-hidden="true"></span>
        <div class="activity-details">
          <p class="activity-text">${message}</p>
          <time class="activity-timestamp">Just now &bull; Console Action</time>
        </div>
      `;
      list.prepend(item);
    }
  };

  /* ===========================================================================
   * 12. UI CONTROLLER (NAVIGATION, TOASTS, NOTIFICATIONS, SHORTCUTS)
   * =========================================================================== */
  const UIController = {
    init() {
      this.bindSidebarNav();
      this.bindGlobalSearch();
      this.bindNotificationsDropdown();
      this.bindUserProfileMenu();
      this.bindHelpModal();
      this.bindKeyboardShortcuts();
    },

    bindSidebarNav() {
      const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
      navLinks.forEach(link => {
        link.addEventListener('click', e => {
          const href = link.getAttribute('href');
          if (href && href.startsWith('#')) {
            e.preventDefault();
            const targetId = href.substring(1);
            const targetElem = document.getElementById(targetId);

            navLinks.forEach(l => {
              l.classList.remove('active');
              l.removeAttribute('aria-current');
            });
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');

            if (targetElem) {
              targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
              targetElem.style.transition = 'box-shadow 0.4s ease';
              targetElem.style.boxShadow = '0 0 20px rgba(34, 211, 238, 0.4)';
              setTimeout(() => {
                targetElem.style.boxShadow = '';
              }, 1200);
            }
          }
        });
      });
    },

    bindGlobalSearch() {
      const searchInput = document.getElementById('global-search-input');
      const searchForm = document.getElementById('global-search-form');

      if (!searchInput || !searchForm) return;

      searchForm.addEventListener('submit', e => {
        e.preventDefault();
        const query = searchInput.value.trim().toLowerCase();
        if (!query) return;

        // Search in local nodes
        const matched = LifeGraphData.nodes.find(n => n.label.toLowerCase().includes(query) || n.uri.toLowerCase().includes(query));
        if (matched) {
          this.showToast(`Found entity: ${matched.label} [${matched.category}]`, 'success');
          // Focus in Cytoscape if active
          if (GraphVisualizer.cy) {
            const cyNode = GraphVisualizer.cy.getElementById(matched.id);
            if (cyNode) {
              GraphVisualizer.cy.animate({ center: { eles: cyNode }, zoom: 1.5, duration: 500 });
              GraphVisualizer.handleNodeSelect(cyNode);
            }
          }
        } else {
          this.showToast(`No exact entity match for "${query}". Redirecting to Vector Search...`, 'info');
          const vecInput = document.getElementById('vector-search-input');
          if (vecInput) {
            vecInput.value = query;
            document.getElementById('vector-search-panel')?.scrollIntoView({ behavior: 'smooth' });
          }
        }
      });
    },

    bindNotificationsDropdown() {
      const notifBtn = document.getElementById('notification-button');
      if (!notifBtn) return;

      notifBtn.addEventListener('click', e => {
        e.stopPropagation();
        let dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
          dropdown.remove();
          return;
        }

        dropdown = document.createElement('div');
        dropdown.id = 'notification-dropdown';
        Object.assign(dropdown.style, {
          position: 'absolute',
          top: '55px',
          right: '28px',
          width: '320px',
          backgroundColor: LifeGraphConfig.colors.bgPanel,
          border: `1px solid ${LifeGraphConfig.colors.borderColor}`,
          borderRadius: '8px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
          zIndex: '999',
          padding: '12px'
        });

        dropdown.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid ${LifeGraphConfig.colors.borderColor}; padding-bottom:8px; margin-bottom:8px;">
            <strong style="font-size:0.85rem; color:#E5EDF7;">System Alerts</strong>
            <button id="btn-clear-notifs" style="background:none; border:none; color:#22D3EE; font-size:0.75rem; cursor:pointer;">Mark all read</button>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px;">
            ${LifeGraphState.notifications.map(n => `
              <div style="padding:8px; background:#0E1726; border-radius:6px; font-size:0.75rem; border:1px solid #26364B;">
                <p style="color:#E5EDF7; font-weight:600; margin-bottom:2px;">${n.title}</p>
                <span style="color:#64748B; font-size:0.7rem;">${n.time} &bull; Neptune Cluster Guard</span>
              </div>
            `).join('')}
          </div>
        `;

        document.body.appendChild(dropdown);

        document.getElementById('btn-clear-notifs')?.addEventListener('click', () => {
          const badge = document.getElementById('notification-badge-count');
          if (badge) badge.style.display = 'none';
          UIController.showToast('All notifications marked as read', 'info');
          dropdown.remove();
        });

        // Close when clicking outside
        const closeListener = evt => {
          if (!dropdown.contains(evt.target) && evt.target !== notifBtn) {
            dropdown.remove();
            document.removeEventListener('click', closeListener);
          }
        };
        setTimeout(() => document.addEventListener('click', closeListener), 10);
      });
    },

    bindUserProfileMenu() {
      const profileBtn = document.getElementById('user-profile-button');
      if (!profileBtn) return;

      profileBtn.addEventListener('click', () => {
        this.showToast('Logged in as Mudasir Reyaz (Lead Graph Architect & Neptune Admin)', 'info');
      });
    },

    bindHelpModal() {
      const helpBtn = document.getElementById('help-button');
      if (!helpBtn) return;

      helpBtn.addEventListener('click', () => {
        alert(
          'LifeGraph AI – Graph + Vector Intelligence Suite\n\n' +
          '• Graph Canvas: Cytoscape.js Force Layout (Tap nodes to inspect 1-hop scope)\n' +
          '• Query Console: Supports Gremlin 3.7, SPARQL 1.1, and openCypher 9\n' +
          '• Vector Search: HNSW Cosine Similarity & Vector Projection\n' +
          '• K-Hop Explorer: Breadth-First-Search Subgraph Expansion\n' +
          '• Backend: Designed for integration with Python FastAPI & Neo4j\n\n' +
          'Shortcut: Press Ctrl + K to focus search.'
        );
      });
    },

    bindKeyboardShortcuts() {
      window.addEventListener('keydown', e => {
        // Ctrl + K or Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
          e.preventDefault();
          const searchInput = document.getElementById('global-search-input');
          if (searchInput) {
            searchInput.focus();
            searchInput.select();
          }
        }
      });
    },

    showToast(message, type = 'info') {
      let toastContainer = document.getElementById('lifegraph-toast-container');
      if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'lifegraph-toast-container';
        Object.assign(toastContainer.style, {
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          zIndex: '9999',
          pointerEvents: 'none'
        });
        document.body.appendChild(toastContainer);
      }

      const toast = document.createElement('div');
      const typeColors = {
        success: LifeGraphConfig.colors.success,
        warning: LifeGraphConfig.colors.warning,
        danger: LifeGraphConfig.colors.danger,
        info: LifeGraphConfig.colors.cyan
      };

      const iconMap = {
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        danger: 'fa-circle-xmark',
        info: 'fa-circle-info'
      };

      const color = typeColors[type] || LifeGraphConfig.colors.cyan;
      const icon = iconMap[type] || 'fa-circle-info';

      Object.assign(toast.style, {
        pointerEvents: 'auto',
        backgroundColor: 'rgba(17, 28, 45, 0.95)',
        borderLeft: `4px solid ${color}`,
        borderTop: '1px solid #26364B',
        borderRight: '1px solid #26364B',
        borderBottom: '1px solid #26364B',
        color: '#E5EDF7',
        padding: '12px 18px',
        borderRadius: '6px',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
        fontSize: '0.82rem',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        maxWidth: '380px',
        backdropFilter: 'blur(8px)',
        transform: 'translateY(20px)',
        opacity: '0',
        transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
      });

      toast.innerHTML = `<i class="fa-solid ${icon}" style="color:${color}; font-size:1.1rem;"></i> <span>${message}</span>`;
      toastContainer.appendChild(toast);

      // Animate in
      requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
      });

      // Auto dismiss after 3.5s
      setTimeout(() => {
        toast.style.transform = 'translateY(10px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 250);
      }, 3500);
    }
  };

  /* ===========================================================================
   * 13. DOM READY INITIALIZATION
   * =========================================================================== */
  document.addEventListener('DOMContentLoaded', async () => {
    console.info(`[LifeGraph AI] Initializing Connected Intelligence Platform v2.4 (Phase 3)...`);

    try {
      UIController.init();
      QueryConsoleManager.init();
      KHopExplorerManager.init();
      VectorSearchManager.init();
      AIIntelligenceManager.init();

      // Initialize Visualizers (handles CDN loading gracefully)
      await GraphVisualizer.init();
      await AnalyticsManager.init();

      console.info(`[LifeGraph AI] Initialization Complete. Ready for Python FastAPI & Neo4j backend integration.`);
    } catch (err) {
      console.error('[LifeGraph AI] Initialization encountered an exception:', err);
    }
  });

})();
