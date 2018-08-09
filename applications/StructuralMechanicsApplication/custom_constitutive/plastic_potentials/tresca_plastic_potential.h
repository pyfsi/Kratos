// KRATOS  ___|  |                   |                   |
//       \___ \  __|  __| |   |  __| __| |   |  __| _` | |
//             | |   |    |   | (    |   |   | |   (   | |
//       _____/ \__|_|   \__,_|\___|\__|\__,_|_|  \__,_|_| MECHANICS
//
//  License:         BSD License
//                   license: structural_mechanics_application/license.txt
//
//  Main authors:    Alejandro Cornejo & Lucia Barbu
//

#if !defined(KRATOS_TRESCA_PLASTIC_POTENTIAL_H_INCLUDED)
#define KRATOS_TRESCA_PLASTIC_POTENTIAL_H_INCLUDED

// System includes

// Project includes
#include "custom_constitutive/plastic_potentials/generic_plastic_potential.h"

namespace Kratos
{
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
 * @class TrescaPlasticPotential
 * @ingroup StructuralMechanicsApplication
 * @brief
 * @details
 * @author Alejandro Cornejo & Lucia Barbu
 */
class KRATOS_API(STRUCTURAL_MECHANICS_APPLICATION) TrescaPlasticPotential
{
  public:
    ///@name Type Definitions
    ///@{

    /// Counted pointer of TrescaPlasticPotential
    KRATOS_CLASS_POINTER_DEFINITION(TrescaPlasticPotential);

    ///@}
    ///@name Life Cycle
    ///@{

    /// Initialization constructor.
    TrescaPlasticPotential()
    {
    }

    /// Copy constructor
    TrescaPlasticPotential(TrescaPlasticPotential const &rOther)
    {
    }

    /// Assignment operator
    TrescaPlasticPotential &operator=(TrescaPlasticPotential const &rOther)
    {
        return *this;
    }

    /// Destructor
    virtual ~TrescaPlasticPotential(){};

    ///@}
    ///@name Operators
    ///@{

    ///@}
    ///@name Operations
    ///@{

    /**
     * @brief This  script  calculates  the derivatives  of the plastic potential
    according   to   NAYAK-ZIENKIEWICZ   paper International
    journal for numerical methods in engineering vol 113-135 1972.
     As:            DF/DS = c1*V1 + c2*V2 + c3*V3
     * @param StressVector The stress vector 
     * @param Deviator The deviatoric part of the stress vector
     * @param J2 The second invariant of the Deviator 
     * @param rGFlux The derivative of the plastic potential
     * @param rMaterialProperties The material properties
     */
    static void CalculatePlasticPotentialDerivative(
        const Vector &StressVector,
        const Vector &Deviator,
        const double J2,
        Vector &rGFlux,
        const Properties &rMaterialProperties)
    {
        Vector first_vector, second_vector, third_vector;

        ConstitutiveLawUtilities::CalculateFirstVector(first_vector);
        ConstitutiveLawUtilities::CalculateSecondVector(Deviator, J2, second_vector);
        ConstitutiveLawUtilities::CalculateThirdVector(Deviator, J2, third_vector);

        double J3, lode_angle;
        ConstitutiveLawUtilities::CalculateJ3Invariant(Deviator, J3);
        ConstitutiveLawUtilities::CalculateLodeAngle(J2, J3, lode_angle);

        const double checker = std::abs(lode_angle * 180.0 / Globals::Pi);

        const double c1 = 0.0;
        double c2, c3;

        if (checker < 29.0)
        {
            c2 = 2.0 * (std::cos(lode_angle) + std::sin(lode_angle) * std::tan(3.0 * lode_angle));
            c3 = std::sqrt(3.0) * std::sin(lode_angle) / (J2 * std::cos(3.0 * lode_angle));
        }
        else
        {
            c2 = std::sqrt(3.0);
            c3 = 0.0;
        }

        noalias(rGFlux) = c1 * first_vector + c2 * second_vector + c3 * third_vector;
    }

    ///@}
    ///@name Access
    ///@{

    ///@}
    ///@name Inquiry
    ///@{

    ///@}
    ///@name Input and output
    ///@{

    ///@}
    ///@name Friends
    ///@{

    ///@}

  protected:
    ///@name Protected static Member Variables
    ///@{

    ///@}
    ///@name Protected member Variables
    ///@{

    ///@}
    ///@name Protected Operators
    ///@{

    ///@}
    ///@name Protected Operations
    ///@{

    ///@}
    ///@name Protected  Access
    ///@{

    ///@}
    ///@name Protected Inquiry
    ///@{

    ///@}
    ///@name Protected LifeCycle
    ///@{

    ///@}

  private:
    ///@name Static Member Variables
    ///@{

    ///@}
    ///@name Member Variables
    ///@{

    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{

    ///@}
    ///@name Private  Access
    ///@{

    ///@}
    ///@name Private Inquiry
    ///@{

    ///@}
    ///@name Un accessible methods
    ///@{

    // Serialization

    friend class Serializer;

    void save(Serializer &rSerializer) const
    {
    }

    void load(Serializer &rSerializer)
    {
    }

    ///@}

}; // Class GenericYieldSurface

///@}

///@name Type Definitions
///@{

///@}
///@name Input and output
///@{

///@}

} // namespace Kratos.
#endif