//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:         BSD License
//                   Kratos default license: kratos/license.txt
//
//  Main author:     Ruben Zorrilla
//
//

#if !defined(KRATOS_FIXED_MESH_ALE_UTILITIES_H_INCLUDED )
#define  KRATOS_FIXED_MESH_ALE_UTILITIES_H_INCLUDED

// System includes


// External includes


// Project includes
#include "includes/define.h"
#include "includes/model_part.h"
#include "linear_solvers/linear_solver.h"
#include "processes/calculate_embedded_nodal_variable_from_skin_process.h"
#include "spaces/ublas_space.h"
#include "solving_strategies/strategies/solving_strategy.h"

// Application includes
#include "custom_strategies/strategies/laplacian_meshmoving_strategy.h"


namespace Kratos
{
///@addtogroup MeshMovingApplication
///@{

///@name Kratos Globals
///@{


///@}
///@name Type Definitions
///@{


///@}
///@name  Enum's
///@{


///@}
///@name  Functions
///@{


///@}
///@name Kratos Classes
///@{

/**
 * @brief Utility to perform the FM-ALE algorithm operations
 * This utility implements the Fixed Mesh - Arbitrary Lagrangian Eulerian (FM-ALE)
 * algorithm operations. After setting a virtual mesh, which is a copy of the
 * problem background element mesh, it is moved in accordante to the immersed
 * object movement. The virtual mesh movement is solved using a common ALE mesh
 * solver (in this case the Laplacian mesh solver is used). Once the mesh movement,
 * including the mesh velocity, have been computed, the origin mesh historical
 * values (velocity and pressure), as well as the mesh velocity, are computed
 * as a projection from the virtual mesh. This is required to consistently
 * initialize the historical values when nodes change its topological status.
 */
class FixedMeshALEUtilities
{
public:
    ///@name Type Definitions
    ///@{

    typedef Element::NodesArrayType NodesArrayType;
    typedef UblasSpace<double, Matrix, Vector> LocalSpaceType;
    typedef UblasSpace<double, CompressedMatrix, Vector> SparseSpaceType;
    typedef LinearSolver<SparseSpaceType, LocalSpaceType> LinearSolverType;
    typedef LaplacianMeshMovingStrategy<SparseSpaceType, LocalSpaceType, LinearSolverType> LaplacianMeshMovingStrategyType;
    typedef CalculateEmbeddedNodalVariableFromSkinProcess<array_1d<double, 3>, SparseSpaceType, LocalSpaceType, LinearSolverType> EmbeddedNodalVariableProcessArrayType;

    /// Pointer definition of FixedMeshALEUtilities
    KRATOS_CLASS_POINTER_DEFINITION(FixedMeshALEUtilities);

    ///@}
    ///@name Life Cycle
    ///@{

    /// Constructor
    FixedMeshALEUtilities(
        ModelPart &rVirtualModelPart,
        ModelPart &rStructureModelPart,
        const std::string LevelSetType);

    /// Destructor.
    ~FixedMeshALEUtilities() {};

    ///@}
    ///@name Operators
    ///@{


    ///@}
    ///@name Operations
    ///@{

    /**
     * @brief Compute the virtual mesh movement
     * This method computes the virtual mesh movement in accordance to the immersed structure
     * DISPLACEMENT values. To that purpose it sets the fixity and creates & solves the
     * mesh moving strategy.
     * @param DeltaTime time step value (required for the computation of the MESH_VELOCITY)
     */
    void ComputeMeshMovement(const double DeltaTime);

    /**
    * This method fills the mrVirtualModelPart with the nodes and elmens of a given model part
    * It has to be performed once since after each values projection the virtual mesh configuration
    * is reverted to its original status.
    * @param rOriginModelPart model part from where the nodes and elements are copied
    */
    void FillVirtualModelPart(ModelPart& rOriginModelPart);

    /**
     * @brief Revert the virtual mesh movement
     * This method reverts the virtual mesh movement to recover its original configuration,
     * which coincides with the background mesh one. It has to be called once the values
     * projection from the virtual mesh to the origin has been performed.
     */
    void UndoMeshMovement();

    /**
     * @brief This method projects the virtual model part mesh values to the origin mesh
     * Once the FM-ALE operations have been performed, this method projects the nodal values
     * from the virtual mesh to the origin mesh. The projected variables are PRESSURE,
     * VELOCITY and MESH_VELOCITY.
     * @tparam TDim Template parameter containing the problem domain size
     * @param rOriginModelPart Reference to the model part to which the values are projected
     * @param BufferSize Buffer values that are projected
     */
    template <unsigned int TDim>
    void ProjectVirtualValues(
        ModelPart &rOriginModelPart,
        const unsigned int BufferSize = 3);

    ///@}
    ///@name Access
    ///@{


    ///@}
    ///@name Inquiry
    ///@{


    ///@}
    ///@name Input and output
    ///@{

    /// Turn back information as a string.
    std::string Info() const;

    /// Print information about this object.
    void PrintInfo(std::ostream& rOStream) const;

    /// Print object's data.
    void PrintData(std::ostream& rOStream) const;

    ///@}
    ///@name Friends
    ///@{


    ///@}
private:
    ///@name Static Member Variables
    ///@{


    ///@}
    ///@name Member Variables
    ///@{

    const std::string mLevelSetType;

    ModelPart &mrVirtualModelPart;
    ModelPart &mrStructureModelPart;
    ModelPart *mpOriginModelPart = nullptr;

    ///@}
    ///@name Private Operators
    ///@{


    ///@}
    ///@name Private Operations
    ///@{

    /**
     * @brief Set the Distances Vector object
     * For an element, this method sets its nodal distances vector.
     * This is done in accordance to mLevelSetType, which contains
     * the level set type (continuous or discontinuous)
     * @param ItElem Iterator to the element to get the distances of
     * @return const Vector Vector containing the elemental nodal distances
     */
    const Vector SetDistancesVector(ModelPart::ElementIterator ItElem);

    /**
     * @brief Check if an element is split
     * From the provided nodal distances vector, this method
     * checks if such element is intersected by the level set
     * @param rDistances Refence to the nodal distances vector
     * @return true If the element is intersected
     * @return false If the element is not intersected
     */
    bool IsSplit(const Vector &rDistances);

    /**
     * @brief Set the virtual mesh origin model part based fixity
     * This method checks the mesh displacement fixity in the origin
     * model part and applies it to the virtual mesh before solving.
     */
    void SetMeshDisplacementFixityFromOriginModelPart();

    /**
     * @brief Set the embedded nodal mesh displacement
     * This method calls the utility that computes the nodal mesh
     * displacement from the immersed structure displacement. Then
     * it fixes such values before the ALE strategy solve call.
     */
    void SetEmbeddedNodalMeshDisplacement();

    /**
     * @brief Set the and solve the mesh movement strategy
     * After all the mesh BCs have been set, this method is called to
     * set and solve the ALE mesh movement strategy. The mesh velocity
     * calculation and virtual mesh update are performe din here.
     * @param DeltaTime time step value (required for the computation of the MESH_VELOCITY)
     */
    void SetAndSolveMeshMovementStrategy(const double DeltaTime);

    ///@}
    ///@name Private  Access
    ///@{


    ///@}
    ///@name Private Inquiry
    ///@{


    ///@}
    ///@name Un accessible methods
    ///@{

    /// Assignment operator.
    FixedMeshALEUtilities& operator=(FixedMeshALEUtilities const& rOther) = delete;

    /// Copy constructor.
    FixedMeshALEUtilities(FixedMeshALEUtilities const& rOther) = delete;

    ///@}
}; // Class FixedMeshALEUtilities

///@}
///@name Input and output
///@{

/// output stream function
inline std::ostream& operator << (
    std::ostream& rOStream,
    const FixedMeshALEUtilities& rThis);

///@}
///@} addtogroup block
}  // namespace Kratos.

#endif // KRATOS_FIXED_MESH_ALE_UTILITIES_H_INCLUDED  defined
