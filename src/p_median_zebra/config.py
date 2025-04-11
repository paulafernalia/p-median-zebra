"""
Defines a Pydantic model for validating parameters used in a p-median problem.

The `ModelParameters` class ensures that inputs such as the number of nodes,
number of depots, map size, and optimization settings meet expected
constraints. It also includes a validator to enforce that the number of depots
does not exceed the number of nodes.

Extra fields are forbidden.
"""

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    conint,
    ValidationInfo,
    ConfigDict,
)


class ModelParameters(BaseModel):
    """
    Represents the configuration parameters for a p-median problem.

    Attributes:
        NNODES (int): Number of nodes in the problem. Must be greater than 1.
        NDEPOTS (int): Number of depots to place. Must be greater than 0 and
                       not exceed NNODES.
        MAPSIZE (int): Size of the map. Must be greater than 0.
        OPT_TIME_LIMIT (float): Maximum time allowed for the optimization
                                process. Must be greater than 0.
        VERBOSE (int): Verbosity flag for logging (0 = silent, 1 = verbose).
                       Must be 0 or 1.

    Constraints:
        - NDEPOTS must not be greater than NNODES.
        - Extra fields not defined in the model are forbidden.

    Validators:
        check_number_depots: Ensures that the number of depots does not exceed
        the number of nodes.
    """

    NNODES: int = Field(..., gt=1, description="Number of nodes (must be > 1)")
    NDEPOTS: int = Field(
        ..., gt=0, description="Number of depots to place (must be > 0)"
    )
    MAPSIZE: int = Field(..., gt=0, description="Size of the map (must be > 0)")

    # Optimization parameters
    OPT_TIME_LIMIT: float = Field(100.0, gt=0, description="Time limit (must be > 1.)")
    VERBOSE: conint(strict=True, ge=0, le=1) = Field(1, description="Must be 0 or 1")

    model_config = ConfigDict(extra="forbid")

    @field_validator("NDEPOTS")
    def check_number_depots(cls, value, info: ValidationInfo):
        """Check that there are no more depots than nodes."""
        if "NNODES" in info.data and value > info.data["NNODES"]:
            raise ValueError("There cannot be more depots than nodes")
        return value
