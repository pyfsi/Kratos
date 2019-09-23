// KRATOS  ___|  |                   |                   |
//       \___ \  __|  __| |   |  __| __| |   |  __| _` | |
//             | |   |    |   | (    |   |   | |   (   | |
//       _____/ \__|_|   \__,_|\___|\__|\__,_|_|  \__,_|_| MECHANICS
//
//  License:		 BSD License
//					 license: StructuralMechanicsApplication/license.txt
//
//  Main authors:    Vicente Mataix Ferrandiz
//


// System includes
#include <unordered_set>

// External includes

// Project includes
#include "contact_structural_mechanics_application_variables.h"
#include "custom_utilities/self_contact_utilities.h"
#include "utilities/variable_utils.h"

namespace Kratos
{
namespace SelfContactUtilities
{
void ComputeSelfContactPairing(ModelPart& rModelPart)
{
    KRATOS_TRY

    // Creating the maps
    std::unordered_set<std::size_t> ids_to_clear;

    // Iterate over the conditions
    auto& r_conditions_array = rModelPart.Conditions();
    const int num_conditions = static_cast<int>(r_conditions_array.size());
    const auto it_cond_begin = r_conditions_array.begin();

    for(int i = 0; i < num_conditions; ++i) {
        auto it_cond = it_cond_begin + i;

        // Checking if already set
        auto p_indexes_pairs = it_cond->GetValue(INDEX_MAP);
        if (it_cond->IsNotDefined(MASTER) || it_cond->IsNot(MASTER)) {
            if (p_indexes_pairs->size() > 0) {
                ids_to_clear.clear();
                for (auto it_pair = p_indexes_pairs->begin(); it_pair != p_indexes_pairs->end(); ++it_pair ) {
                    const IndexType master_id = p_indexes_pairs->GetId(it_pair); // MASTER
                    auto p_master_cond = rModelPart.pGetCondition(master_id);
                    auto& r_master_geometry = p_master_cond->GetGeometry();

                    // Iterate over nodes
                    std::size_t counter = 0;
                    for (auto& r_node : r_master_geometry) {
                        if (r_node.IsNotDefined(MASTER) || r_node.Is(MASTER)) {
                            ++counter;
                        }
                    }

                    // Assign flags
                    if (counter == r_master_geometry.size()) {
                        p_master_cond->Set(MASTER, true);
                        p_master_cond->Set(SLAVE, false);
                        for (auto& r_node : r_master_geometry) {
                            r_node.Set(MASTER, true);
                            r_node.Set(SLAVE, false);
                        }
                    } else {
                        ids_to_clear.insert(master_id);
                    }
                }
                for (std::size_t id : ids_to_clear) {
                    p_indexes_pairs->RemoveId(id);
                }
            }
            // Assigning SLAVE flags
            if (p_indexes_pairs->size() > 0) {
                it_cond->Set(MASTER, false);
                it_cond->Set(SLAVE, true);
                for (auto& r_node : it_cond->GetGeometry()) {
                    r_node.Set(MASTER, false);
                    r_node.Set(SLAVE, true);
                }
            }
        } else { // If master we clear
            p_indexes_pairs->clear();
        }
    }

    KRATOS_CATCH("")
}

/***********************************************************************************/
/***********************************************************************************/

void NotPredefinedMasterSlave(ModelPart& rModelPart)
{
    KRATOS_TRY

    // We iterate over the conditions
    auto& r_conditions_array = rModelPart.Conditions();
    const auto it_cond_begin = r_conditions_array.begin();
    const int num_conditions = static_cast<int>(r_conditions_array.size());

    std::vector<IndexType> master_conditions_ids;

    #pragma omp parallel
    {
        // Creating a buffer for parallel vector fill
        std::vector<IndexType> master_conditions_ids_buffer;

        #pragma omp for
        for(int i = 0; i < num_conditions; ++i) {
            auto it_cond = it_cond_begin + i;
            IndexMap::Pointer p_indexes_pairs = it_cond->GetValue(INDEX_MAP);
            if (p_indexes_pairs->size() > 0) {
                it_cond->Set(SLAVE, true);
                for (auto& i_pair : *p_indexes_pairs) {
                    master_conditions_ids_buffer.push_back(i_pair.first);
                }
            }
        }

        // Combine buffers together
        #pragma omp critical
        {
            std::move(master_conditions_ids_buffer.begin(),master_conditions_ids_buffer.end(),back_inserter(master_conditions_ids));
        }
    }

    // We create an auxiliar model part to add the MASTER flag
    rModelPart.CreateSubModelPart("AuxMasterModelPart");
    ModelPart& aux_model_part = rModelPart.GetSubModelPart("AuxMasterModelPart");

    // Remove duplicates
    std::sort( master_conditions_ids.begin(), master_conditions_ids.end() );
    master_conditions_ids.erase( std::unique( master_conditions_ids.begin(), master_conditions_ids.end() ), master_conditions_ids.end() );

    // Add to the auxiliar model part
    aux_model_part.AddConditions(master_conditions_ids);

    // Set the flag
    VariableUtils().SetFlag(MASTER, true, aux_model_part.Conditions());

    // Remove auxiliar model part
    rModelPart.RemoveSubModelPart("AuxMasterModelPart");

    // Now we iterate over the conditions to set the nodes indexes
    #pragma omp parallel for
    for(int i = 0; i < num_conditions; ++i) {
        auto it_cond = r_conditions_array.begin() + i;
        if (it_cond->Is(SLAVE)) {
            GeometryType& r_geometry = it_cond->GetGeometry();
            for (NodeType& r_node : r_geometry) {
                r_node.SetLock();
                r_node.Set(SLAVE, true);
                r_node.UnSetLock();
            }
        }
        if (it_cond->Is(MASTER)) {
            GeometryType& r_geometry = it_cond->GetGeometry();
            for (NodeType& r_node : r_geometry) {
                r_node.SetLock();
                r_node.Set(MASTER, true);
                r_node.UnSetLock();
            }
        }
    }

    KRATOS_CATCH("")
}


} // namespace SelfContactUtilities
} // namespace Kratos
