(function () {
  const canvas = document.getElementById('renderCanvas');
  const engine = new BABYLON.Engine(canvas, true, {
    preserveDrawingBuffer: true,
    stencil: true,
    antialias: true,
    deterministicLockstep: false,
    powerPreference: 'high-performance',
  });

  const state = {
    renderScale: 1,
    hdrEnabled: true,
    pipeline: null,
    character: null,
    animationGroups: [],
    input: { forward: false, back: false, left: false, right: false, dash: false },
    velocity: new BABYLON.Vector3(0, 0, 0),
    targetSpeed: 7,
    dashSpeed: 20,
    dashCooldown: 0,
  };

  function setHardwareScalingFor4K(scale) {
    // Lower hardware scaling for higher resolution rendering. scale = 1 means native pixel ratio
    engine.setHardwareScalingLevel(1 / (window.devicePixelRatio * scale));
    document.getElementById('resLabel').textContent = `${Math.round(window.innerWidth * window.devicePixelRatio * scale)}x${Math.round(window.innerHeight * window.devicePixelRatio * scale)}`;
  }

  function createScene() {
    const scene = new BABYLON.Scene(engine);
    scene.useRightHandedSystem = true;
    scene.autoClear = true;
    scene.createDefaultLight(true);
    scene.gravity = new BABYLON.Vector3(0, -9.81, 0);

    // Environment
    const env = scene.createDefaultEnvironment({
      createSkybox: true,
      skyboxSize: 2000,
      enableGroundShadow: true,
      groundSize: 2000,
    });

    // PBR defaults
    scene.environmentIntensity = 1.0;

    // Post-processing pipeline
    state.pipeline = new BABYLON.DefaultRenderingPipeline('default', state.hdrEnabled, scene, scene.cameras);
    state.pipeline.samples = 4; // MSAA
    state.pipeline.bloomEnabled = true;
    state.pipeline.bloomThreshold = 0.7;
    state.pipeline.bloomWeight = 0.35;
    state.pipeline.bloomKernel = 64;
    state.pipeline.imageProcessingEnabled = true;
    state.pipeline.imageProcessing.contrast = 1.05;
    state.pipeline.imageProcessing.exposure = 1.1;
    state.pipeline.sharpenEnabled = true;

    // Camera (Follow)
    const cameraTarget = new BABYLON.TransformNode('cameraTarget', scene);
    const camera = new BABYLON.FollowCamera('follow', new BABYLON.Vector3(0, 2, -6), scene);
    camera.lockedTarget = cameraTarget;
    camera.radius = 6.5;
    camera.heightOffset = 2.2;
    camera.rotationOffset = 180;
    camera.cameraAcceleration = 0.05;
    camera.maxCameraSpeed = 20;

    // Light
    const hemi = new BABYLON.HemisphericLight('hemi', new BABYLON.Vector3(0.4, 1, 0.2), scene);
    hemi.intensity = 0.85;

    const dir = new BABYLON.DirectionalLight('dir', new BABYLON.Vector3(-0.5, -1, 0.4), scene);
    dir.position = new BABYLON.Vector3(30, 60, -30);
    dir.intensity = 2.2;
    const shadowGen = new BABYLON.ShadowGenerator(4096, dir);
    shadowGen.usePercentageCloserFiltering = true;
    shadowGen.bias = 0.0005;

    // Ground
    const ground = BABYLON.MeshBuilder.CreateGround('ground', { width: 2000, height: 2000, subdivisions: 64 }, scene);
    const groundMat = new BABYLON.PBRMaterial('groundMat', scene);
    groundMat.albedoColor = new BABYLON.Color3(0.28, 0.3, 0.32);
    groundMat.roughness = 0.8;
    ground.material = groundMat;
    ground.receiveShadows = true;

    // Load character (Khronos CesiumMan as placeholder)
    const characterRoot = new BABYLON.TransformNode('characterRoot', scene);
    BABYLON.SceneLoader.ImportMesh('', 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/CesiumMan/glTF/', 'CesiumMan.gltf', scene, (meshes, particleSystems, skeletons, animationGroups) => {
      const rootMesh = new BABYLON.TransformNode('hero', scene);
      meshes.forEach(m => {
        if (m.material && m.material.getClassName && m.material.getClassName() === 'PBRMaterial') {
          m.material.maxSimultaneousLights = 8;
        }
        m.receiveShadows = true;
        shadowGen.addShadowCaster(m, true);
        m.parent = rootMesh;
        m.scaling.scaleInPlace(1.2);
      });
      rootMesh.parent = characterRoot;
      rootMesh.position = new BABYLON.Vector3(0, 0, 0);

      state.character = rootMesh;
      state.animationGroups = animationGroups || [];
      state.animationGroups.forEach(ag => ag.start(true));

      cameraTarget.parent = state.character;
      cameraTarget.position = new BABYLON.Vector3(0, 1.6, 0);
    });

    // Simple input
    attachInput(scene);

    // Game loop
    scene.onBeforeRenderObservable.add(() => {
      const dt = scene.getEngine().getDeltaTime() / 1000;
      updateCharacter(dt);
      updateStats();
    });

    return scene;
  }

  function attachInput(scene) {
    window.addEventListener('keydown', (e) => {
      if (e.repeat) return;
      if (e.code === 'KeyW') state.input.forward = true;
      if (e.code === 'KeyS') state.input.back = true;
      if (e.code === 'KeyA') state.input.left = true;
      if (e.code === 'KeyD') state.input.right = true;
      if (e.code === 'Space') state.input.dash = true;
    });
    window.addEventListener('keyup', (e) => {
      if (e.code === 'KeyW') state.input.forward = false;
      if (e.code === 'KeyS') state.input.back = false;
      if (e.code === 'KeyA') state.input.left = false;
      if (e.code === 'KeyD') state.input.right = false;
      if (e.code === 'Space') state.input.dash = false;
    });

    // Pointer lock for mouse look via camera rotation around target
    canvas.addEventListener('click', () => canvas.requestPointerLock?.());
    window.addEventListener('mousemove', (e) => {
      if (document.pointerLockElement !== canvas) return;
      const rotY = -e.movementX * 0.1;
      const rotX = -e.movementY * 0.05;
      const scene = engine.scenes[0];
      const camera = scene.activeCamera;
      camera.rotationOffset = (camera.rotationOffset + rotY) % 360;
      camera.heightOffset = BABYLON.Scalar.Clamp(camera.heightOffset + rotX * 0.05, 1.2, 4.0);
    });
  }

  function updateCharacter(dt) {
    if (!state.character) return;

    // movement direction in camera space
    const scene = engine.scenes[0];
    const camera = scene.activeCamera;
    const forward = new BABYLON.Vector3(
      Math.sin(BABYLON.Tools.ToRadians(camera.rotationOffset)),
      0,
      Math.cos(BABYLON.Tools.ToRadians(camera.rotationOffset))
    ).normalize();
    const right = new BABYLON.Vector3(forward.z, 0, -forward.x);

    let move = new BABYLON.Vector3(0, 0, 0);
    if (state.input.forward) move.addInPlace(forward);
    if (state.input.back) move.subtractInPlace(forward);
    if (state.input.right) move.addInPlace(right);
    if (state.input.left) move.subtractInPlace(right);
    if (move.lengthSquared() > 0.0001) move.normalize();

    let speed = state.targetSpeed;
    if (state.input.dash && state.dashCooldown <= 0) {
      speed = state.dashSpeed;
      state.dashCooldown = 0.5; // seconds
    }
    state.dashCooldown = Math.max(0, state.dashCooldown - dt);

    const displacement = move.scale(speed * dt);
    state.character.position.addInPlace(displacement);

    if (move.lengthSquared() > 0) {
      const targetYawDeg = Math.atan2(move.x, move.z) * 180 / Math.PI;
      const currentYawDeg = state.character.rotation.y * 180 / Math.PI;
      const newYaw = BABYLON.Scalar.LerpAngle(currentYawDeg, targetYawDeg, 0.2);
      state.character.rotation.y = newYaw * Math.PI / 180;
    }
  }

  function updateStats() {
    const fps = Math.round(engine.getFps());
    document.getElementById('fps').textContent = fps.toString();
  }

  // Quality presets
  function applyPreset(preset) {
    switch (preset) {
      case 'max':
        state.hdrEnabled = true;
        if (state.pipeline) state.pipeline.samples = 8;
        setHardwareScalingFor4K(1.25); // render over native for extra sharpness if GPU allows
        break;
      case 'balanced':
        state.hdrEnabled = true;
        if (state.pipeline) state.pipeline.samples = 4;
        setHardwareScalingFor4K(1.0);
        break;
      case 'performance':
        state.hdrEnabled = false;
        if (state.pipeline) state.pipeline.samples = 1;
        setHardwareScalingFor4K(0.66);
        break;
    }
    if (state.pipeline) state.pipeline.hdr = state.hdrEnabled;
  }

  function bindUI() {
    document.getElementById('btnMax').addEventListener('click', () => applyPreset('max'));
    document.getElementById('btnBalanced').addEventListener('click', () => applyPreset('balanced'));
    document.getElementById('btnPerformance').addEventListener('click', () => applyPreset('performance'));
    document.getElementById('btnToggleHDR').addEventListener('click', () => {
      state.hdrEnabled = !state.hdrEnabled;
      if (state.pipeline) state.pipeline.hdr = state.hdrEnabled;
    });
  }

  const scene = createScene();
  bindUI();

  setHardwareScalingFor4K(1.0);

  engine.runRenderLoop(() => {
    scene.render();
  });

  window.addEventListener('resize', () => {
    engine.resize();
    setHardwareScalingFor4K(state.renderScale || 1.0);
  });
})();