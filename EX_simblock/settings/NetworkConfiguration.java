/*
 * Copyright 2019 Distributed Systems Group
 *
 * <p>Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * <p>http://www.apache.org/licenses/LICENSE-2.0
 *
 * <p>Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package simblock.settings;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** ネットワークの遅延と帯域幅を設定するためのネットワーク構成クラス */
public class NetworkConfiguration {
  /** ノードが存在可能な地域 */
  public static final List<String> REGION_LIST =
      new ArrayList<>(
          Arrays.asList(
              "NORTH_AMERICA", "EUROPE", "SOUTH_AMERICA", "ASIA_PACIFIC", "JAPAN", "AUSTRALIA"));

  /**
   * LATENCY[i][j] は2015年時点での REGION_LIST[i] から REGION_LIST[j] への平均遅延（単位：ミリ秒）
   */
  private static final long[][] LATENCY_2015 = {
    {36, 119, 255, 310, 154, 208},
    {119, 12, 221, 242, 266, 350},
    {255, 221, 137, 347, 256, 269},
    {310, 242, 347, 99, 172, 278},
    {154, 266, 256, 172, 9, 163},
    {208, 350, 269, 278, 163, 22}
  };
  /**
   * LATENCY[i][j] は2019年時点での REGION_LIST[i] から REGION_LIST[j] への平均遅延（単位：ミリ秒）
   */
  private static final long[][] LATENCY_2019 = {
    {32, 124, 184, 198, 151, 189},
    {124, 11, 227, 237, 252, 294},
    {184, 227, 88, 325, 301, 322},
    {198, 237, 325, 85, 58, 198},
    {151, 252, 301, 58, 12, 126},
    {189, 294, 322, 198, 126, 16}
  };

  /** 地域ごとに割り当てられた遅延のリスト（単位：ミリ秒） */
  public static final long[][] LATENCY = LATENCY_2019;

  /**
   * 2015年の地域ごとのダウンロード帯域幅と地域間帯域幅（単位：ビット毎秒）
   */
  private static final long[] DOWNLOAD_BANDWIDTH_2015 = {
    25000000, 24000000, 6500000, 10000000, 17500000, 14000000, 6 * 1000000
  };
  /**
   * 2019年の地域ごとのダウンロード帯域幅と地域間帯域幅（単位：ビット毎秒）
   */
  private static final long[] DOWNLOAD_BANDWIDTH_2019 = {
    52000000, 40000000, 18000000, 22800000, 22800000, 29900000, 6 * 1000000
  };

  /** 地域ごとのダウンロード帯域幅と地域間帯域幅（単位：ビット毎秒） */
  public static final long[] DOWNLOAD_BANDWIDTH = DOWNLOAD_BANDWIDTH_2019;

  /**
   * 2015年の地域ごとのアップロード帯域幅と地域間帯域幅（単位：ビット毎秒）
   */
  private static final long[] UPLOAD_BANDWIDTH_2015 = {
    4700000, 8100000, 1800000, 5300000, 3400000, 5200000, 6 * 1000000
  };

  /**
   * 2019年の地域ごとのアップロード帯域幅と地域間帯域幅（単位：ビット毎秒）
   */
  private static final long[] UPLOAD_BANDWIDTH_2019 = {
    19200000, 20700000, 5800000, 15700000, 10200000, 11300000, 6 * 1000000
  };

  /** 地域ごとのアップロード帯域幅と地域間帯域幅（単位：ビット毎秒） */
  public static final long[] UPLOAD_BANDWIDTH = UPLOAD_BANDWIDTH_2019;

  /** 2015年のビットコインの地域分布 */
  private static final double[] REGION_DISTRIBUTION_BITCOIN_2015 = {
    0.3869, 0.5159, 0.0113,
    0.0574, 0.0119, 0.0166
  };

  /** 2019年のビットコインの地域分布 */
  private static final double[] REGION_DISTRIBUTION_BITCOIN_2019 = {
    0.3316, 0.4998, 0.0090,
    0.1177, 0.0224, 0.0195
  };

  /** ライトコインの地域分布（年次未指定） */
  private static final double[] REGION_DISTRIBUTION_LITECOIN = {
    0.3661, 0.4791, 0.0149, 0.1022, 0.0238, 0.0139
  };

  /** ドージコインの地域分布（年次未指定） */
  private static final double[] REGION_DISTRIBUTION_DOGECOIN = {
    0.3924, 0.4879, 0.0212, 0.0697, 0.0106, 0.0182
  };

  /** ノードの地域分布（地域ごとのノード数の割合） */
  public static final double[] REGION_DISTRIBUTION = REGION_DISTRIBUTION_BITCOIN_2019;

  /** 2015年のビットコインのアウトバウンドリンク数の累積分布 */
  private static final double[] DEGREE_DISTRIBUTION_BITCOIN_2015 = {
    0.025, 0.050, 0.075, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 0.97,
    0.97, 0.98, 0.99, 0.995, 1.0
  };

  /** アウトバウンドリンク数の累積分布（ビットコイン2015年のデータを使用） */
  public static final double[] DEGREE_DISTRIBUTION = DEGREE_DISTRIBUTION_BITCOIN_2015;
}
