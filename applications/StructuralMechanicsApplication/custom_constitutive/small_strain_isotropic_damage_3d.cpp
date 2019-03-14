// KRATOS  ___|  |                   |                   |
//       \___ \  __|  __| |   |  __| __| |   |  __| _` | |
//             | |   |    |   | (    |   |   | |   (   | |
//       _____/ \__|_|   \__,_|\___|\__|\__,_|_|  \__,_|_| MECHANICS
//
//  License:		 BSD License
//					 license: structural_mechanics_application/license.txt
//
//  Main authors:    Marcelo Raschi
//  Collaborators:
//

// Project includes
#include "small_strain_isotropic_damage_3d.h"
#include "structural_mechanics_application_variables.h"
#include "includes/checks.h"

namespace Kratos
{
//******************************CONSTRUCTOR*******************************************
//************************************************************************************

SmallStrainIsotropicDamage3D::SmallStrainIsotropicDamage3D()
    : ElasticIsotropic3D()
{
}

//********************************COPY CONSTRUCTOR************************************
//************************************************************************************

SmallStrainIsotropicDamage3D::SmallStrainIsotropicDamage3D(const SmallStrainIsotropicDamage3D &rOther)
    : ElasticIsotropic3D(rOther)
{
}

//********************************CLONE***********************************************
//************************************************************************************

ConstitutiveLaw::Pointer SmallStrainIsotropicDamage3D::Clone() const
{
    return Kratos::make_shared<SmallStrainIsotropicDamage3D>(SmallStrainIsotropicDamage3D(*this));
}

//********************************DESTRUCTOR******************************************
//************************************************************************************

SmallStrainIsotropicDamage3D::~SmallStrainIsotropicDamage3D()
{
}

//************************************************************************************
//************************************************************************************

bool SmallStrainIsotropicDamage3D::Has(const Variable<bool>& rThisVariable)
{
    if(rThisVariable == INELASTIC_FLAG){
        return true;
    }
    return false;
}

//************************************************************************************
//************************************************************************************

bool SmallStrainIsotropicDamage3D::Has(const Variable<double>& rThisVariable)
{
    return false;
}

//************************************************************************************
//************************************************************************************

bool& SmallStrainIsotropicDamage3D::GetValue(
    const Variable<bool>& rThisVariable,
    bool& rValue
    )
{
    if(rThisVariable == INELASTIC_FLAG){
        rValue = mInelasticFlag;
    }

    return rValue;
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::InitializeMaterial(
    const Properties& rMaterialProperties,
    const GeometryType& rElementGeometry,
    const Vector& rShapeFunctionsValues
    )
{
    const double yield_stress = rMaterialProperties[YIELD_STRESS];
    const double young_modulus = rMaterialProperties[YOUNG_MODULUS];
    mStrainVariable = yield_stress / std::sqrt(young_modulus);
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::InitializeMaterialResponseCauchy(ConstitutiveLaw::Parameters& rValues)
{
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::FinalizeMaterialResponseCauchy(Parameters& rValues)
{
    double strain_variable;
    this->CalculateStressResponse(rValues, strain_variable);
    mStrainVariable = strain_variable;
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::CalculateMaterialResponsePK2(Parameters& rValues)
{
    double strain_variable;
    this->CalculateStressResponse(rValues, strain_variable);
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::CalculateStressResponse(
        Parameters &rValues,
        double &rStrainVariable)
{
    const Properties& rMaterialProperties = rValues.GetMaterialProperties();
    Flags & r_constitutive_law_options = rValues.GetOptions();
    Vector& r_strain_vector = rValues.GetStrainVector();
    if (rValues.GetProcessInfo().Has(INITIAL_STRAIN)) {
        noalias(r_strain_vector) += rValues.GetProcessInfo()[INITIAL_STRAIN];
    }

    if( r_constitutive_law_options.IsNot( ConstitutiveLaw::USE_ELEMENT_PROVIDED_STRAIN )) {
        //this->CalculateValue(rValues, STRAIN, r_strain_vector);
    }

    // If we compute the tangent moduli or the stress
    if( r_constitutive_law_options.Is( ConstitutiveLaw::COMPUTE_STRESS ) ||
        r_constitutive_law_options.Is( ConstitutiveLaw::COMPUTE_CONSTITUTIVE_TENSOR )) {
        Vector& r_stress_vector = rValues.GetStressVector();
        Matrix& r_constitutive_matrix = rValues.GetConstitutiveMatrix();
        CalculateElasticMatrix(r_constitutive_matrix, rValues);
        noalias(r_stress_vector) = prod(r_constitutive_matrix, r_strain_vector);

        // Auxiliary stress vector to allow derived models (e.g. traction-only damage) to set
        // a different value of r_stress_vector_pos with ComputePositiveStressVector function
        // In the symmetric model, ComputePositiveStressVector does not do anything.
        Vector r_stress_vector_pos = r_stress_vector;
        ComputePositiveStressVector(r_stress_vector_pos, r_stress_vector);

        const double strain_norm = std::sqrt(inner_prod(r_stress_vector_pos, r_strain_vector));
        if (strain_norm <= mStrainVariable)
        {
            // ELASTIC
            mInelasticFlag = false;
            rStrainVariable = mStrainVariable;
            const double stress_variable = EvaluateHardeningLaw(rStrainVariable, rMaterialProperties);
            const double damage_variable = 1. - stress_variable / rStrainVariable;
            r_constitutive_matrix *= (1 - damage_variable);
            r_stress_vector *= (1 - damage_variable);
        }
        else
        {
            // INELASTIC
            mInelasticFlag = true;
            rStrainVariable = strain_norm;
            const double stress_variable = EvaluateHardeningLaw(rStrainVariable, rMaterialProperties);
            const double damage_variable = 1. - stress_variable / rStrainVariable;
            const double hardening_modulus = rMaterialProperties[ISOTROPIC_HARDENING_MODULUS];
            const double damage_rate = (stress_variable - hardening_modulus * rStrainVariable)
                                       / (rStrainVariable * rStrainVariable * rStrainVariable);
            r_constitutive_matrix *= (1. - damage_variable);
            r_constitutive_matrix -= damage_rate * outer_prod(r_stress_vector_pos, r_stress_vector);
            r_stress_vector *= (1. - damage_variable);
        }
    }
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::ComputePositiveStressVector(
            Vector& rStressVectorPos, Vector& rStressVector)
{
}

//************************************************************************************
//************************************************************************************

double& SmallStrainIsotropicDamage3D::CalculateValue(
    Parameters& rValues,
    const Variable<double>& rThisVariable,
    double& rValue
    )
{
    if (rThisVariable == STRAIN_ENERGY){
        Vector& r_strain_vector = rValues.GetStrainVector();
        if (rValues.GetProcessInfo().Has(INITIAL_STRAIN)) {
            noalias(r_strain_vector) += rValues.GetProcessInfo()[INITIAL_STRAIN];
        }
        const Properties& rMaterialProperties = rValues.GetMaterialProperties();
        Matrix& constitutive_matrix = rValues.GetConstitutiveMatrix();
        CalculateElasticMatrix(constitutive_matrix, rValues);
        const double stress_like_variable = EvaluateHardeningLaw(mStrainVariable, rMaterialProperties);
        const double damage_variable = 1. - stress_like_variable / mStrainVariable;

        rValue = 0.5 * ((1. - damage_variable) * inner_prod(r_strain_vector,
                                              prod(constitutive_matrix, r_strain_vector)));
    }

    if (rThisVariable == DAMAGE_VARIABLE){
        const Properties& rMaterialProperties = rValues.GetMaterialProperties();
        const double stress_like_variable = EvaluateHardeningLaw(mStrainVariable, rMaterialProperties);

        rValue = 1. - stress_like_variable / mStrainVariable;
    }

    return(rValue);
}

//************************************************************************************
//************************************************************************************

double SmallStrainIsotropicDamage3D::EvaluateHardeningLaw(
        double StrainVariable,
        const Properties &rMaterialProperties)
{
    const double yield_stress = rMaterialProperties[YIELD_STRESS];
    const double inf_yield_stress = rMaterialProperties[INFINITY_YIELD_STRESS];
    const double young_modulus = rMaterialProperties[YOUNG_MODULUS];
    const double hardening_modulus = rMaterialProperties[ISOTROPIC_HARDENING_MODULUS];
    const double strain_variable_init = yield_stress / std::sqrt(young_modulus);
    const double stress_variable_inf = inf_yield_stress / std::sqrt(young_modulus);
    double stress_variable;
    const double tolerance = std::numeric_limits<double>::epsilon();

    if (StrainVariable < strain_variable_init)
        return strain_variable_init;
    stress_variable = strain_variable_init + hardening_modulus * (StrainVariable - strain_variable_init);
    if ((hardening_modulus > tolerance && stress_variable > stress_variable_inf) ||
        (hardening_modulus < tolerance && stress_variable < stress_variable_inf))
        stress_variable = stress_variable_inf;
    return stress_variable;
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::GetLawFeatures(Features& rFeatures)
{
    rFeatures.mOptions.Set(THREE_DIMENSIONAL_LAW);
    rFeatures.mOptions.Set(INFINITESIMAL_STRAINS);
    rFeatures.mOptions.Set(ISOTROPIC);
    rFeatures.mStrainMeasures.push_back(StrainMeasure_Infinitesimal);
    rFeatures.mStrainSize = this->GetStrainSize();
    rFeatures.mSpaceDimension = this->WorkingSpaceDimension();
}

//************************************************************************************
//************************************************************************************

int SmallStrainIsotropicDamage3D::Check(
    const Properties& rMaterialProperties,
    const GeometryType& rElementGeometry,
    const ProcessInfo& rCurrentProcessInfo
    )
{
    const double tolerance = std::numeric_limits<double>::epsilon();

    KRATOS_CHECK(rMaterialProperties.Has(YOUNG_MODULUS));
    KRATOS_CHECK(rMaterialProperties.Has(POISSON_RATIO));
    KRATOS_CHECK(rMaterialProperties.Has(YIELD_STRESS));
    KRATOS_CHECK(rMaterialProperties.Has(INFINITY_YIELD_STRESS));
    KRATOS_CHECK(rMaterialProperties.Has(ISOTROPIC_HARDENING_MODULUS));
    KRATOS_CHECK_GREATER(rMaterialProperties[YIELD_STRESS], tolerance);
    KRATOS_CHECK_GREATER(rMaterialProperties[INFINITY_YIELD_STRESS], tolerance);
    KRATOS_CHECK_LESS(rMaterialProperties[ISOTROPIC_HARDENING_MODULUS], 1.);
    KRATOS_CHECK_NOT_EQUAL(rMaterialProperties[ISOTROPIC_HARDENING_MODULUS], tolerance);

    if (rMaterialProperties[ISOTROPIC_HARDENING_MODULUS] > tolerance &&
        rMaterialProperties[INFINITY_YIELD_STRESS] <= rMaterialProperties[YIELD_STRESS])
        KRATOS_ERROR << "If ISOTROPIC_HARDENING_MODULUS is positive, "
            "INFINITY_YIELD_STRESS must be greater than YIELD_STRESS" << std::endl;

    if (rMaterialProperties[ISOTROPIC_HARDENING_MODULUS] < tolerance &&
        rMaterialProperties[INFINITY_YIELD_STRESS] >= rMaterialProperties[YIELD_STRESS])
        KRATOS_ERROR << "If ISOTROPIC_HARDENING_MODULUS is negative, "
                "INFINITY_YIELD_STRESS must be lesser than YIELD_STRESS" << std::endl;

    return 0;
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::save(Serializer& rSerializer) const
{
    KRATOS_SERIALIZE_SAVE_BASE_CLASS(rSerializer, ConstitutiveLaw);
    rSerializer.save("mInelasticFlag", mInelasticFlag);
    rSerializer.save("mStrainVariable", mStrainVariable);
}

//************************************************************************************
//************************************************************************************

void SmallStrainIsotropicDamage3D::load(Serializer& rSerializer)
{
    KRATOS_SERIALIZE_LOAD_BASE_CLASS(rSerializer, ConstitutiveLaw);
    rSerializer.load("mInelasticFlag", mInelasticFlag);
    rSerializer.save("mStrainVariable", mStrainVariable);
}

} /* namespace Kratos.*/
