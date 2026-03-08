from gdsfactory.technology import LayerStack
from gdsfactory.technology.layer_stack import LayerLevel

from lightly_engineered.config import StackConfig
from lightly_engineered.pdk.layers import LAYER


def get_layer_stack(cfg: StackConfig | None = None) -> LayerStack:
    cfg = cfg or StackConfig()
    rib_height = cfg.si_thickness_um - cfg.slab_thickness_um

    return LayerStack(
        layers=dict(
            substrate=LayerLevel(
                layer=LAYER.WAFER,
                zmin=-(cfg.box_thickness_um + 10.0),
                thickness=10.0,
                material="si",
                mesh_order=99,
            ),
            box=LayerLevel(
                layer=LAYER.BOX,
                zmin=-cfg.box_thickness_um,
                thickness=cfg.box_thickness_um,
                material="sio2",
                mesh_order=98,
            ),
            slab=LayerLevel(
                layer=LAYER.SLAB,
                zmin=0.0,
                thickness=cfg.slab_thickness_um,
                material="si",
                mesh_order=2,
            ),
            core=LayerLevel(
                layer=LAYER.WG,
                zmin=cfg.slab_thickness_um,
                thickness=rib_height,
                material="si",
                mesh_order=1,
            ),
            clad=LayerLevel(
                layer=LAYER.CLAD,
                zmin=cfg.si_thickness_um,
                thickness=cfg.top_clad_thickness_um,
                material="sio2",
                mesh_order=100,
            ),
            m1=LayerLevel(
                layer=LAYER.M1,
                zmin=1.2,
                thickness=0.6,
                material="Al",
                mesh_order=10,
            ),
            m2=LayerLevel(
                layer=LAYER.M2,
                zmin=2.2,
                thickness=1.2,
                material="Al",
                mesh_order=11,
            ),
        )
    )
