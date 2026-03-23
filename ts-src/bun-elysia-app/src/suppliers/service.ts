// Suppliers service - Scoring engine logic
// Translated from scoring_engine.py

import { prisma } from "../config/database";
import {
  SupplierScore,
  LeaderboardEntry,
  FarmDescription,
  EligibilityData,
  QualityAudit,
  LocationData,
} from "../types";

export class SupplierService {
  /**
   * Main scoring calculation function
   * Translates calculate_scores() from scoring_engine.py
   */
  async calculateScores(): Promise<void> {
    try {
      // STEP 1: GET THE DATA
      // Join transactions with suppliers to get all necessary fields
      const transactions = await prisma.transaction.findMany({
        include: {
          supplier: true,
        },
        orderBy: {
          date: "asc",
        },
      });

      if (transactions.length === 0) {
        console.log("⚠️ No matching data found. Did you run the Seeder?");
        return;
      }

      // STEP 2: GROUP BY SUPPLIER AND CALCULATE SCORES
      const supplierGroups = this.groupTransactionsBySupplier(transactions);
      const supplierScores: SupplierScore[] = [];

      for (const [supplierId, group] of Object.entries(supplierGroups)) {
        // A. SEASONALITY - Based on recency of last delivery
        const lastDelivery = new Date(
          Math.max(...group.map((t) => t.date.getTime()))
        );
        const seasonalityScore = this.calculateSeasonalityScore(lastDelivery);

        // B. VOLUME - Based on delivered vs expected yield
        const farmData = group[0].supplier.description as FarmDescription;
        const bearingTrees = farmData?.bearing_trees || 100;
        const totalDelivered = group.reduce((sum, t) => sum + t.amount, 0);
        const volumeScore = this.calculateVolumeScore(
          totalDelivered,
          bearingTrees
        );

        // C. QUALITY - Based on audit results
        const qualityAudits = group
          .map((t) => t.quality as QualityAudit | null)
          .filter((q): q is QualityAudit => q !== null);
        const qualityScore = this.calculateQualityScore(qualityAudits);

        // D. PHILGAP - Certification compliance
        const eligibility = group[0].supplier.eligibility as EligibilityData;
        const philgapScore = this.calculatePhilGAPScore(
          eligibility?.philgap_certified || false
        );

        // FORMULA: Weighted average
        const finalScore =
          seasonalityScore * 0.4 +
          volumeScore * 0.3 +
          qualityScore * 0.2 +
          philgapScore * 0.1;

        supplierScores.push({
          supplier_id: supplierId,
          score: Math.round(finalScore),
        });
      }

      // STEP 3: UPDATE THE DATABASE
      console.log(
        `--- UPDATING SCORES for ${supplierScores.length} Suppliers ---`
      );

      // Update all scores in a transaction
      await prisma.$transaction(
        supplierScores.map((item) =>
          prisma.supplier.update({
            where: { supplier_id: item.supplier_id },
            data: { reliability_score: item.score },
          })
        )
      );

      console.log("✅ Database update successful.");
    } catch (error) {
      console.error(`❌ Critical Error in Scoring Engine: ${error}`);
      throw error;
    }
  }

  /**
   * Fetch leaderboard sorted by reliability score
   */
  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    const suppliers = await prisma.supplier.findMany({
      orderBy: {
        reliability_score: "desc",
      },
    });

    return suppliers.map((s) => ({
      supplier_id: s.supplier_id,
      name: s.name,
      location: s.location as LocationData,
      reliability_score: s.reliability_score,
      description: s.description as FarmDescription,
      eligibility: s.eligibility as EligibilityData,
    }));
  }

  /**
   * Calculate seasonality score based on delivery recency
   * Score decreases by 2 points per day since last delivery
   */
  private calculateSeasonalityScore(lastDelivery: Date): number {
    const now = new Date();
    const daysSince = Math.floor(
      (now.getTime() - lastDelivery.getTime()) / (1000 * 60 * 60 * 24)
    );
    return Math.max(0, 100 - daysSince * 2);
  }

  /**
   * Calculate volume score based on delivered vs expected yield
   * Expected yield = bearing_trees * 2.0 kg
   */
  private calculateVolumeScore(
    totalDelivered: number,
    bearingTrees: number
  ): number {
    const expectedYield = Math.max(bearingTrees * 2.0, 1); // Prevent division by zero
    return Math.min(100, (totalDelivered / expectedYield) * 100);
  }

  /**
   * Calculate quality score based on audit results
   * Deductions for mold, insect damage, and moisture content
   */
  private calculateQualityScore(audits: QualityAudit[]): number {
    if (audits.length === 0) return 0;

    const qualityScores = audits.map((audit) => {
      let score = 100;
      const cutTest = audit.cut_test_results;

      // Deductions based on quality metrics
      if (cutTest && cutTest.moldy_percent > 3.0) score -= 40;
      if (cutTest && cutTest.insect_damaged_percent > 2.5) score -= 20;

      const moistureContent = audit.moisture_content || audit.moisture || 7.0;
      if (moistureContent > 8.0) score -= 20;

      return Math.max(0, score);
    });

    return (
      qualityScores.reduce((sum, score) => sum + score, 0) / qualityScores.length
    );
  }

  /**
   * Calculate PhilGAP certification score
   * Binary: 100 if certified, 0 if not
   */
  private calculatePhilGAPScore(certified: boolean): number {
    return certified ? 100 : 0;
  }

  /**
   * Group transactions by supplier ID
   */
  private groupTransactionsBySupplier(transactions: any[]): {
    [key: string]: any[];
  } {
    return transactions.reduce((groups, transaction) => {
      const supplierId = transaction.supplier_id;
      if (!groups[supplierId]) {
        groups[supplierId] = [];
      }
      groups[supplierId].push(transaction);
      return groups;
    }, {} as { [key: string]: any[] });
  }
}
